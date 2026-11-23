/**
 * Race Expert AI - Storefront & Interactive Consultation Drawer
 * Visual Identity: Pure Race Expert Brand
 * Functional Pattern: Left Drawer with Suggested Chips & Typewriter Streaming
 */

// Elements - Drawer & Controls
const drawer = document.getElementById("ai-drawer");
const backdrop = document.getElementById("drawer-backdrop");
const btnTriggerAi = document.getElementById("btn-trigger-ai");
const btnFloatingAi = document.getElementById("btn-floating-ai");
const btnTabTriggerAi = document.getElementById("btn-tab-trigger-ai");
const btnDrawerClose = document.getElementById("btn-drawer-close");
const drawerBody = document.getElementById("drawer-body");

// Elements - Article Switcher in Drawer
const drawerSkuInput = document.getElementById("drawer-sku-input");
const btnLoadSku = document.getElementById("btn-load-sku");
const artChips = document.querySelectorAll(".art-chip");

// Elements - Drawer Product Preview Card
const drawerProductImg = document.getElementById("drawer-product-img");
const drawerProductTitle = document.getElementById("drawer-product-title");
const drawerProductPrice = document.getElementById("drawer-product-price");
const drawerStockBadge = document.getElementById("drawer-stock-badge");

// Elements - Showcase Storefront Page
const showcaseTitle = document.getElementById("showcase-title");
const showcaseSku = document.getElementById("showcase-sku");
const specsSku = document.getElementById("specs-sku");
const showcasePrice = document.getElementById("showcase-price");
const showcaseDescription = document.getElementById("showcase-description");
const showcaseStockLabel = document.getElementById("showcase-stock-label");
const mainProductImg = document.getElementById("main-product-img");
const breadcrumbProductName = document.getElementById("breadcrumb-product-name");

// Elements - Chat & Composer
const chatMessages = document.getElementById("chat-messages");
const typingIndicator = document.getElementById("typing-indicator");
const composerForm = document.getElementById("chat-composer-form");
const composerInput = document.getElementById("composer-user-input");
const suggestedChipsFlow = document.getElementById("suggested-chips-flow");

// Quantity Spinner
const qtyMinus = document.getElementById("qty-minus");
const qtyPlus = document.getElementById("qty-plus");
const qtyVal = document.getElementById("qty-val");

// State
let currentProduct = null;
let isGenerating = false;
let dialogHistory = [];
const WAITING_COPY = "Готуємо відповідь про вибраний товар…";

// Product Images Mapping
const DEMO_IMAGES = {
  RE0126: "static/images/RE0126.jpg",
  RE1050: "static/images/RE1050.png",
  RE0518: "static/images/RE0518.jpg",
  RE0508: "static/images/RE0508.jpg",
  RE0537: "static/images/RE0537.png",
  RE0731: "static/images/RE0731.jpg",
};

// --- Drawer Open / Close Functions ---
function openDrawer() {
  if (!drawer || !backdrop) return;
  drawer.classList.add("is-open");
  backdrop.classList.add("is-active");
  drawer.setAttribute("aria-hidden", "false");
  document.body.style.overflow = "hidden";
  setTimeout(() => composerInput && composerInput.focus(), 250);
}

function closeDrawer() {
  if (!drawer || !backdrop) return;
  drawer.classList.remove("is-open");
  backdrop.classList.remove("is-active");
  drawer.setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";
}

// Drawer Listeners
if (btnTriggerAi) btnTriggerAi.addEventListener("click", openDrawer);
if (btnFloatingAi) btnFloatingAi.addEventListener("click", openDrawer);
if (btnTabTriggerAi) btnTabTriggerAi.addEventListener("click", openDrawer);
if (btnDrawerClose) btnDrawerClose.addEventListener("click", closeDrawer);
if (backdrop) backdrop.addEventListener("click", closeDrawer);

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && drawer && drawer.classList.contains("is-open")) {
    closeDrawer();
  }
});

// --- Product Loading & Switching ---
async function loadProductByArticle(article) {
  const cleanArticle = (article || "").trim().toUpperCase();
  if (!cleanArticle) return;

  if (btnLoadSku) {
    btnLoadSku.disabled = true;
    btnLoadSku.textContent = "Пошук...";
  }

  try {
    const res = await fetch(`api/search?article=${encodeURIComponent(cleanArticle)}`);
    if (!res.ok) throw new Error("Помилка завантаження");
    const data = await res.json();

    let product = null;
    if (data.status === "single" && data.product) {
      product = data.product;
    } else if (data.status === "ambiguous" && data.candidates && data.candidates.length > 0) {
      product = data.candidates[0];
    }

    if (product) {
      currentProduct = product;
      dialogHistory = [];
      renderProduct(product);
      updateActiveChip(cleanArticle);
    } else {
      alert(`Товар з артикулом "${cleanArticle}" не знайдено в каталозі OpenCart.`);
    }
  } catch (err) {
    console.error("Search error:", err);
    alert("Не вдалося завантажити товар. Перевірте з'єднання із сервером.");
  } finally {
    if (btnLoadSku) {
      btnLoadSku.disabled = false;
      btnLoadSku.textContent = "Знайти";
    }
  }
}

function renderProduct(product) {
  const ukCard = (product.languages && product.languages.uk) || (product.languages && product.languages.ru) || {};
  const name = ukCard.name || product.model || product.article;
  const article = product.article || product.model || "";
  const stock = ukCard.stock_label || "Є в наявності";
  const desc = ukCard.description || "Опис товару доступний за запитом.";
  const imgUrl = DEMO_IMAGES[article] || "https://placehold.co/600x600/f8fafc/253237?text=Race+Expert";

  // Update Drawer Mini Card
  if (drawerProductTitle) drawerProductTitle.textContent = name;
  if (drawerProductImg) drawerProductImg.src = imgUrl;
  if (drawerStockBadge) drawerStockBadge.textContent = stock;
  if (drawerSkuInput) drawerSkuInput.value = article;

  // Update Storefront Page
  if (showcaseTitle) showcaseTitle.textContent = name;
  if (showcaseSku) showcaseSku.textContent = article;
  if (specsSku) specsSku.textContent = article;
  if (breadcrumbProductName) breadcrumbProductName.textContent = name;
  if (showcaseStockLabel) showcaseStockLabel.textContent = stock;
  if (mainProductImg) mainProductImg.src = imgUrl;
  if (showcaseDescription) showcaseDescription.textContent = desc;

  // Price formatting
  const price = article === "RE0126" ? "2299" : (article === "RE0731" ? "108" : "1150");
  if (showcasePrice) showcasePrice.textContent = price;
  if (drawerProductPrice) drawerProductPrice.textContent = `${price} грн`;

  // Render Suggested Quick Questions (6 per group/subgroup)
  renderSuggestedQuestions(product.suggested_questions);
}

function renderSuggestedQuestions(questions) {
  const container = document.querySelector(".suggested-chips-flow") || document.getElementById("suggested-chips-flow");
  if (!container) return;
  const list = Array.isArray(questions) && questions.length > 0 ? questions : [
    "Як правильно застосовувати цей товар за інструкцією виробника?",
    "Які головні переваги та особливості цього продукту?",
    "Для яких видів тренувань або цілей він підходить найкраще?",
    "Який точний склад, вага та розмір цієї упаковки?",
    "Чи є додаткові смаки або варіанти цього товару в наявності?",
    "Чи сумісний цей товар з іншим щоденним спортивним харчуванням?"
  ];

  container.innerHTML = "";
  list.forEach((q) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "prompt-chip";
    btn.setAttribute("data-question", q);
    btn.textContent = q;
    btn.addEventListener("click", () => {
      askQuestion(q);
    });
    container.appendChild(btn);
  });
}

function updateActiveChip(article) {
  artChips.forEach((chip) => {
    if (chip.getAttribute("data-article") === article) {
      chip.classList.add("active");
    } else {
      chip.classList.remove("active");
    }
  });
}

// Article Search Events
if (btnLoadSku) {
  btnLoadSku.addEventListener("click", () => {
    loadProductByArticle(drawerSkuInput.value);
  });
}

if (drawerSkuInput) {
  drawerSkuInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      loadProductByArticle(drawerSkuInput.value);
    }
  });
}

artChips.forEach((chip) => {
  chip.addEventListener("click", () => {
    const art = chip.getAttribute("data-article");
    if (art) loadProductByArticle(art);
  });
});

// --- Typing Indicator Helpers ---
function showTypingIndicator() {
  if (!typingIndicator) return;
  typingIndicator.removeAttribute("hidden");
  typingIndicator.classList.add("is-active");
  typingIndicator.style.setProperty("display", "flex", "important");
  scrollDrawerToBottom();
}

function hideTypingIndicator() {
  if (!typingIndicator) return;
  typingIndicator.setAttribute("hidden", "true");
  typingIndicator.classList.remove("is-active");
  typingIndicator.style.setProperty("display", "none", "important");
}

// Dialog Context Helper
function formatQuestionWithHistory(rawQuestion, history) {
  const current = (rawQuestion || "").trim();
  if (!history || history.length === 0) {
    return current;
  }
  const recentTurns = history.slice(-3);
  let contextStr = "Контекст попередньої розмови:\n";
  for (const turn of recentTurns) {
    contextStr += `- Покупець: ${turn.question}\n`;
    contextStr += `- Консультант: ${turn.answer}\n`;
  }
  contextStr += `\nПоточне повідомлення покупця: ${current}`;

  if (contextStr.length > 1850) {
    const lastTurn = recentTurns[recentTurns.length - 1];
    return `Контекст попередньої розмови:\n- Покупець: ${lastTurn.question}\n- Консультант: ${lastTurn.answer}\n\nПоточне повідомлення покупця: ${current}`;
  }
  return contextStr;
}

// --- Chat & Questions Handling ---
async function askQuestion(questionText) {
  const text = (questionText || "").trim();
  if (!text || isGenerating || !currentProduct) return;

  isGenerating = true;

  // 1. Append User Message
  appendUserMessage(text);
  if (composerInput) composerInput.value = "";

  // 2. Show Typing Indicator
  showTypingIndicator();

  try {
    const questionWithContext = formatQuestionWithHistory(text, dialogHistory);

    const payload = {
      article: currentProduct.article,
      product_id: currentProduct.product_id,
      question: questionWithContext,
    };

    const res = await fetch("api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    hideTypingIndicator();

    if (res.ok && data.attempt && data.attempt.answer) {
      dialogHistory.push({
        question: text,
        answer: data.attempt.answer,
      });
      await appendAssistantMessageWithTypewriter(data.attempt.answer);
    } else if (data.error) {
      appendAssistantMessage(mapErrorMessage(data.error));
    } else {
      appendAssistantMessage("Не вдалося сформувати відповідь. Будь ласка, спробуйте ще раз або зверніться до менеджера Race Expert.");
    }
  } catch (err) {
    console.error("Ask error:", err);
    hideTypingIndicator();
    appendAssistantMessage("Сталася тимчасова помилка зв'язку із сервером відповідей. Спробуйте ще раз через хвилину.");
  } finally {
    hideTypingIndicator();
    isGenerating = false;
    scrollDrawerToBottom();
  }
}

function mapErrorMessage(code) {
  switch (code) {
    case "product_not_found":
      return "Інформацію про цей товар не знайдено в базі даних Race Expert.";
    case "rate_limited":
      return "Забагато запитань за короткий час. Будь ласка, зачекайте хвилину перед наступним запитанням.";
    case "request_too_large":
      return "Ваше запитання занадто велике за обсягом. Сформулюйте його коротше.";
    case "catalog_unavailable":
      return "База даних OpenCart тимчасово недоступна. Будь ласка, спробуйте пізніше.";
    default:
      return "Наразі не вдалося сформувати відповідь. Будь ласка, перефразуйте запитання.";
  }
}

function appendUserMessage(text) {
  const msgRow = document.createElement("div");
  msgRow.className = "message-bubble user-bubble";

  const content = document.createElement("div");
  content.className = "bubble-content";

  const bubbleText = document.createElement("div");
  bubbleText.className = "bubble-text";
  bubbleText.textContent = text;

  content.appendChild(bubbleText);
  msgRow.appendChild(content);
  chatMessages.appendChild(msgRow);
  scrollDrawerToBottom();
}

async function appendAssistantMessageWithTypewriter(fullText) {
  const msgRow = document.createElement("div");
  msgRow.className = "message-bubble assistant-bubble";

  const avatar = document.createElement("div");
  avatar.className = "bubble-avatar";
  avatar.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M12 2L14.4 9.6L22 12L14.4 14.4L12 22L9.6 14.4L2 12L9.6 9.6L12 2Z" fill="#3960FF"/></svg>`;

  const content = document.createElement("div");
  content.className = "bubble-content";

  const bubbleText = document.createElement("div");
  bubbleText.className = "bubble-text";

  content.appendChild(bubbleText);
  msgRow.appendChild(avatar);
  msgRow.appendChild(content);
  chatMessages.appendChild(msgRow);

  // Fast typewriter streaming
  const words = fullText.split(" ");
  let currentString = "";

  for (let i = 0; i < words.length; i++) {
    currentString += (i > 0 ? " " : "") + words[i];
    bubbleText.textContent = currentString;
    scrollDrawerToBottom();
    await new Promise((resolve) => setTimeout(resolve, 18));
  }
}

function appendAssistantMessage(fullText) {
  const msgRow = document.createElement("div");
  msgRow.className = "message-bubble assistant-bubble";

  const avatar = document.createElement("div");
  avatar.className = "bubble-avatar";
  avatar.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M12 2L14.4 9.6L22 12L14.4 14.4L12 22L9.6 14.4L2 12L9.6 9.6L12 2Z" fill="#3960FF"/></svg>`;

  const content = document.createElement("div");
  content.className = "bubble-content";

  const bubbleText = document.createElement("div");
  bubbleText.className = "bubble-text";
  bubbleText.textContent = fullText;

  content.appendChild(bubbleText);
  msgRow.appendChild(avatar);
  msgRow.appendChild(content);
  chatMessages.appendChild(msgRow);
  scrollDrawerToBottom();
}

function scrollDrawerToBottom() {
  if (drawerBody) {
    drawerBody.scrollTop = drawerBody.scrollHeight;
  }
}

// Suggested Prompt Chips (bind initial chips)
if (suggestedChipsFlow) {
  suggestedChipsFlow.querySelectorAll(".prompt-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const q = chip.getAttribute("data-question");
      if (q) askQuestion(q);
    });
  });
}

// Composer Form Submit
if (composerForm) {
  composerForm.addEventListener("submit", (e) => {
    e.preventDefault();
    if (composerInput) askQuestion(composerInput.value);
  });
}

// Action Chips
const chipClearChat = document.getElementById("chip-clear-chat");
if (chipClearChat) {
  chipClearChat.addEventListener("click", () => {
    dialogHistory = [];
    hideTypingIndicator();
    chatMessages.innerHTML = `
      <div class="message-bubble assistant-bubble">
        <div class="bubble-avatar">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M12 2L14.4 9.6L22 12L14.4 14.4L12 22L9.6 14.4L2 12L9.6 9.6L12 2Z" fill="#3960FF"/></svg>
        </div>
        <div class="bubble-content">
          <div class="bubble-text">Діалог очищено. Поставте нове запитання про обраний товар або оберіть підказку вище.</div>
        </div>
      </div>
    `;
  });
}

const chipShowDesc = document.getElementById("chip-show-desc");
if (chipShowDesc) {
  chipShowDesc.addEventListener("click", () => {
    askQuestion("Коротко опиши цей товар та його головні переваги за описом.");
  });
}

const chipShowFacts = document.getElementById("chip-show-facts");
if (chipShowFacts) {
  chipShowFacts.addEventListener("click", () => {
    askQuestion("Які точні характеристики, об'єм та форма випуску зазначені в картці?");
  });
}

// Main Page Tabs Switching
const tabButtons = document.querySelectorAll(".tab-nav-btn, .tab-btn");
const tabContents = document.querySelectorAll(".tab-pane, .tab-content");

tabButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    const targetTab = btn.getAttribute("data-tab");
    tabButtons.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");

    tabContents.forEach((c) => {
      c.hidden = c.id !== `tab-${targetTab}`;
    });
  });
});

// Quantity Spinner Logic
if (qtyMinus && qtyPlus && qtyVal) {
  qtyMinus.addEventListener("click", () => {
    let cur = parseInt(qtyVal.value, 10) || 1;
    if (cur > 1) qtyVal.value = cur - 1;
  });
  qtyPlus.addEventListener("click", () => {
    let cur = parseInt(qtyVal.value, 10) || 1;
    qtyVal.value = cur + 1;
  });
}

// Flavor Variation Chips
const varChips = document.querySelectorAll(".var-chip");
varChips.forEach((chip) => {
  chip.addEventListener("click", () => {
    varChips.forEach((c) => c.classList.remove("active"));
    chip.classList.add("active");
  });
});

// Initial Product Load on Page Startup
window.addEventListener("DOMContentLoaded", () => {
  hideTypingIndicator();
  loadProductByArticle("RE0126");
});
