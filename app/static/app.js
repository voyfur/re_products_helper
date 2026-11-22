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
const suggestionChips = document.querySelectorAll(".suggestion-chip");

let selectedProduct = null;
let searchToken = 0;

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

function renderAnswer(attempt) {
  latestAnswer.replaceChildren();
  latestAnswer.dataset.status = attempt.status;
  latestAnswer.hidden = false;
  latestAnswer.append(
    textElement("p", "answer-kicker", attempt.status === "succeeded" ? "ВІДПОВІДЬ" : "СТАН ЗАПИТУ"),
    textElement(
      "p",
      "answer-text",
      attempt.answer || "Запит збережено, але відповідь отримати не вдалося. Спробуйте ще раз.",
    ),
  );
}

questionForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const question = questionInput.value.trim();
  if (!selectedProduct || !question) return;

  askButton.disabled = true;
  questionInput.disabled = true;
  searchButton.disabled = true;
  latestAnswer.hidden = true;
  setMessage(questionMessage, "Готуємо відповідь про вибраний товар…");

  try {
    const response = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({
        article: selectedProduct.article,
        product_id: selectedProduct.product_id,
        question,
      }),
    });
    const body = await response.json();
    if (!response.ok) {
      const messages = {
        product_selection_required: "Вибраний товар змінився. Знайдіть його ще раз.",
        product_not_found: "Товар більше не знайдено. Виконайте пошук ще раз.",
        catalog_unavailable: "Каталог тимчасово недоступний. Спробуйте пізніше.",
      };
      setMessage(questionMessage, messages[body.error] || "Не вдалося надіслати запитання. Спробуйте ще раз.", "error");
      return;
    }
    renderAnswer(body.attempt);
    setMessage(
      questionMessage,
      body.attempt.status === "succeeded" ? "Готово." : "Не вдалося отримати відповідь.",
      body.attempt.status === "succeeded" ? "success" : "error",
    );
  } catch {
    setMessage(questionMessage, "Не вдалося зв’язатися із сервісом. Перевірте підключення й повторіть спробу.", "error");
  } finally {
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
