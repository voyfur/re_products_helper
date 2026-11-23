const searchForm = document.querySelector("#search-form");
const articleInput = document.querySelector("#article-input");
const searchButton = document.querySelector("#search-button");
const searchMessage = document.querySelector("#search-message");
const candidateList = document.querySelector("#candidate-list");
const productPanel = document.querySelector("#product-panel");
const productTitle = document.querySelector("#product-title");
const productCode = document.querySelector("#product-code");
const productStock = document.querySelector("#product-stock");
const productDescription = document.querySelector("#product-description");
const productFacts = document.querySelector("#product-facts");
const productAttributes = document.querySelector("#product-attributes");
const questionForm = document.querySelector("#question-form");
const questionInput = document.querySelector("#question-input");
const questionCounter = document.querySelector("#question-counter");
const askButton = document.querySelector("#ask-button");
const questionMessage = document.querySelector("#question-message");
const latestAnswer = document.querySelector("#latest-answer");
const typingIndicator = document.querySelector("#typing-indicator");
const suggestionChips = document.querySelectorAll(".suggestion-chip");

let selectedProduct = null;
let searchToken = 0;
let conversationHistory = [];
let activeAnswerText = null;
let activeAskController = null;

function setMessage(node, text, kind = "") {
  node.textContent = text;
  node.className = kind ? "message " + kind : "message";
}

function textElement(tag, className, value) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  node.textContent = value || "";
  return node;
}

function ukrainianCard(product) {
  return product.languages && product.languages.uk;
}

function productName(product) {
  const card = ukrainianCard(product);
  return (card && card.name) || product.model || product.sku || product.article;
}

function productCodeLine(product) {
  return [
    product.article && "Артикул " + product.article,
    product.model && product.model !== product.article && "Модель " + product.model,
    product.sku && "SKU " + product.sku,
  ].filter(Boolean).join(" · ");
}

function renderProduct(product) {
  if (!selectedProduct || selectedProduct.product_id !== product.product_id) {
    conversationHistory = [];
  }
  selectedProduct = product;
  const card = ukrainianCard(product);
  productPanel.hidden = false;
  productTitle.textContent = productName(product);
  productCode.textContent = productCodeLine(product);

  productStock.textContent = card && card.stock_label ? card.stock_label : "";
  productStock.hidden = !productStock.textContent;

  productDescription.textContent = card && card.description ? card.description : "";
  productDescription.hidden = !productDescription.textContent;

  productAttributes.replaceChildren();
  const attributes = ((card && card.attributes) || []).filter(
    (attribute) => !["артикул", "модель", "sku"].includes((attribute.name || "").trim().toLowerCase()),
  );
  attributes.forEach((attribute) => {
    productAttributes.append(
      textElement("dt", "", attribute.name),
      textElement("dd", "", attribute.value),
    );
  });
  productFacts.hidden = attributes.length === 0;

  questionInput.disabled = false;
  askButton.disabled = false;
  latestAnswer.hidden = true;
  latestAnswer.replaceChildren();
  activeAnswerText = null;
  typingIndicator.hidden = true;
  questionInput.value = "";
  updateQuestionCounter();
  setMessage(questionMessage, "");
}

function renderCandidates(products) {
  candidateList.replaceChildren();
  products.forEach((product) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "candidate-option";
    button.append(
      textElement("strong", "", productName(product)),
      textElement("span", "candidate-meta", productCodeLine(product)),
    );
    button.addEventListener("click", () => {
      candidateList.hidden = true;
      renderProduct(product);
      setMessage(searchMessage, "Товар вибрано.", "success");
    });
    candidateList.append(button);
  });
  candidateList.hidden = false;
}

async function searchProduct(article) {
  const token = ++searchToken;
  if (activeAskController) {
    activeAskController.abort();
    activeAskController = null;
  }
  conversationHistory = [];
  selectedProduct = null;
  productPanel.hidden = true;
  candidateList.replaceChildren();
  candidateList.hidden = true;
  searchButton.disabled = true;
  setMessage(searchMessage, "Шукаємо точний збіг…");

  try {
    const response = await fetch("/api/search?article=" + encodeURIComponent(article), {
      headers: { Accept: "application/json" },
    });
    const result = await response.json();
    if (token !== searchToken) return;
    if (!response.ok) throw new Error(result.error || "catalog_unavailable");

    if (result.status === "not_found") {
      setMessage(searchMessage, "Збігів немає. Перевірте введені дані й повторіть пошук.", "error");
    } else if (result.status === "single") {
      renderProduct(result.product);
      setMessage(searchMessage, "Товар підтверджено.", "success");
    } else if (result.status === "ambiguous") {
      renderCandidates(result.candidates || []);
      setMessage(searchMessage, "Є кілька точних збігів. Виберіть потрібний товар.", "error");
    } else {
      throw new Error("catalog_unavailable");
    }
  } catch {
    if (token === searchToken) {
      setMessage(searchMessage, "Не вдалося виконати пошук. Перевірте підключення й повторіть спробу.", "error");
    }
  } finally {
    if (token === searchToken) searchButton.disabled = false;
  }
}

searchForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const article = articleInput.value.trim();
  if (article) void searchProduct(article);
});

function updateQuestionCounter() {
  questionCounter.textContent = questionInput.value.length + " / 2000";
}

questionInput.addEventListener("input", updateQuestionCounter);

suggestionChips.forEach((chip) => {
  chip.addEventListener("click", () => {
    if (!selectedProduct) return;
    questionInput.value = chip.textContent.trim();
    updateQuestionCounter();
    questionInput.focus();
  });
});

function prepareAnswer() {
  if (activeAnswerText) return;
  latestAnswer.replaceChildren();
  latestAnswer.dataset.status = "succeeded";
  latestAnswer.hidden = false;
  latestAnswer.append(
    textElement("p", "answer-kicker", "ВІДПОВІДЬ"),
    textElement("p", "answer-text", ""),
  );
  activeAnswerText = latestAnswer.querySelector(".answer-text");
}

function appendAnswerDelta(text) {
  prepareAnswer();
  activeAnswerText.textContent += text;
}

function replaceAnswer(answer) {
  prepareAnswer();
  activeAnswerText.textContent = answer;
}

function clearPartialAnswer() {
  latestAnswer.replaceChildren();
  latestAnswer.hidden = true;
  activeAnswerText = null;
}

async function readSseStream(response, onEvent) {
  if (!response.body || !response.body.getReader) {
    throw new Error("answer_unavailable");
  }
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  function dispatchFrame(frame) {
    let eventName = "message";
    const dataLines = [];
    frame.split("\n").forEach((line) => {
      if (line.startsWith("event:")) eventName = line.slice(6).trim();
      if (line.startsWith("data:")) dataLines.push(line.slice(5).trimStart());
    });
    if (!dataLines.length) return;
    onEvent(eventName, JSON.parse(dataLines.join("\n")));
  }

  while (true) {
    const { value, done } = await reader.read();
    buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
    buffer = buffer.replace(/\r\n/g, "\n");
    let boundary = buffer.indexOf("\n\n");
    while (boundary >= 0) {
      dispatchFrame(buffer.slice(0, boundary));
      buffer = buffer.slice(boundary + 2);
      boundary = buffer.indexOf("\n\n");
    }
    if (done) break;
  }
  if (buffer.trim()) dispatchFrame(buffer);
}

function askRequestBody(question) {
  const payload = {
    article: selectedProduct.article,
    product_id: selectedProduct.product_id,
    question,
    history: conversationHistory.slice(-9).map(({ role, content }) => ({ role, content })),
  };
  let body = JSON.stringify(payload);
  while (new TextEncoder().encode(body).length > 16_384 && payload.history.length > 0) {
    payload.history.shift();
    body = JSON.stringify(payload);
  }
  return body;
}

questionForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const question = questionInput.value.trim();
  if (!selectedProduct || !question) return;
  const submittedProductId = selectedProduct.product_id;
  const controller = new AbortController();
  activeAskController = controller;

  askButton.disabled = true;
  questionInput.disabled = true;
  searchButton.disabled = true;
  latestAnswer.hidden = true;
  latestAnswer.replaceChildren();
  activeAnswerText = null;
  typingIndicator.hidden = false;
  setMessage(questionMessage, "Готуємо відповідь про вибраний товар…");

  try {
    const response = await fetch("/api/ask/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
      body: askRequestBody(question),
      signal: controller.signal,
    });
    if (!response.ok) {
      const body = await response.json();
      const messages = {
        product_selection_required: "Вибраний товар змінився. Знайдіть його ще раз.",
        product_not_found: "Товар більше не знайдено. Виконайте пошук ще раз.",
        catalog_unavailable: "Каталог тимчасово недоступний. Спробуйте пізніше.",
      };
      setMessage(questionMessage, messages[body.error] || "Не вдалося надіслати запитання. Спробуйте ще раз.", "error");
      return;
    }
    if (!(response.headers.get("content-type") || "").includes("text/event-stream")) {
      throw new Error("answer_unavailable");
    }
    let completed = false;
    let failed = false;
    await readSseStream(response, (eventName, payload) => {
      if (eventName === "delta" && typeof payload.text === "string") {
        appendAnswerDelta(payload.text);
      } else if (eventName === "replace" && typeof payload.answer === "string") {
        replaceAnswer(payload.answer);
      } else if (eventName === "done" && payload.status === "succeeded") {
        completed = true;
      } else if (eventName === "error") {
        failed = true;
        clearPartialAnswer();
      }
    });
    if (failed || !completed) {
      clearPartialAnswer();
      setMessage(questionMessage, "Не вдалося отримати відповідь. Спробуйте ще раз.", "error");
      return;
    }
    if (!selectedProduct || selectedProduct.product_id !== submittedProductId) return;
    const answer = activeAnswerText ? activeAnswerText.textContent : "";
    if (answer) {
      conversationHistory.push(
        { role: "user", content: question },
        { role: "assistant", content: answer },
      );
      conversationHistory = conversationHistory.slice(-10);
    }
    setMessage(questionMessage, "Готово.", "success");
  } catch (error) {
    if (error.name === "AbortError") return;
    clearPartialAnswer();
    setMessage(questionMessage, "Не вдалося зв’язатися із сервісом. Перевірте підключення й повторіть спробу.", "error");
  } finally {
    if (activeAskController === controller) activeAskController = null;
    if (selectedProduct && selectedProduct.product_id === submittedProductId) {
      typingIndicator.hidden = true;
    }
    questionInput.disabled = !selectedProduct;
    askButton.disabled = !selectedProduct;
    searchButton.disabled = false;
  }
});

const initialArticle = new URLSearchParams(window.location.search).get("article");
if (initialArticle && initialArticle.trim()) {
  articleInput.value = initialArticle.trim();
  void searchProduct(articleInput.value);
}
