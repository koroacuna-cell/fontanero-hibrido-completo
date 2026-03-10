// Manejo de pantallas
const screens = document.querySelectorAll(".screen");
document.querySelectorAll(".viñeta").forEach((item) => {
  item.addEventListener("click", () => {
    screens.forEach((s) => s.classList.remove("active"));
    const target = item.getAttribute("data-screen");
    document.getElementById(target).classList.add("active");
    if (target === "chat") initWelcomeMessage();
  });
});

// Cargar imágenes con detalles y botones
function cargarItems(carpeta, listaId) {
  const lista = document.getElementById(listaId);

  fetch(carpeta)
    .then((res) => res.text())
    .then((text) => {
      const parser = new DOMParser();
      const doc = parser.parseFromString(text, "text/html");
      const links = Array.from(doc.querySelectorAll("a"));

      links.forEach((link) => {
        const href = link.getAttribute("href");
        if (href.match(/\.(png|jpg|jpeg|gif)$/i)) {
          const li = document.createElement("li");

          const img = document.createElement("img");
          img.src = carpeta + "/" + href;

          const details = document.createElement("div");
          details.className = "item-details";

          const name = document.createElement("div");
          name.className = "item-name";
          name.textContent = href.split(".")[0];

          const price = document.createElement("div");
          price.className = "item-price";
          price.textContent = "Precio: €0,00";

          const desc = document.createElement("div");
          desc.className = "item-description";
          desc.textContent = "Descripción técnica y medidas del producto.";

          const btnWhats = document.createElement("button");
          btnWhats.textContent = "Contactar WhatsApp";
          btnWhats.onclick = () =>
            window.open(
              `https://wa.me/34611844783?text=Hola,+estoy+interesado+en+${encodeURIComponent(
                href
              )}`,
              "_blank"
            );

          const btnFV = document.createElement("button");
          btnFV.textContent = "Preguntar al Fontanero";
          btnFV.className = "fv-btn";
          btnFV.onclick = () => {
            screens.forEach((s) => s.classList.remove("active"));
            document.getElementById("chat").classList.add("active");
            userInput.value = href.split(".")[0];
            sendBtn.click();
          };

          details.appendChild(name);
          details.appendChild(price);
          details.appendChild(desc);
          details.appendChild(btnWhats);
          details.appendChild(btnFV);

          li.appendChild(img);
          li.appendChild(details);
          lista.appendChild(li);
        }
      });
    })
    .catch((err) =>
      console.warn(
        "No se pueden listar imágenes desde la carpeta:",
        carpeta
      )
    );
}

cargarItems("img/productos", "productos-list");
cargarItems("img/ofertas", "ofertas-list");
cargarItems("img/productos/novedades", "novedades-list");

// Zoom de imagen
document.addEventListener("click", (e) => {
  if (
    e.target.tagName === "IMG" &&
    (e.target.closest("#productos-list") ||
      e.target.closest("#ofertas-list") ||
      e.target.closest("#novedades-list"))
  ) {
    const modal = document.createElement("div");
    modal.style.position = "fixed";
    modal.style.top = 0;
    modal.style.left = 0;
    modal.style.width = "100%";
    modal.style.height = "100%";
    modal.style.background = "rgba(0, 0, 0, 0.8)";
    modal.style.display = "flex";
    modal.style.justifyContent = "center";
    modal.style.alignItems = "center";
    modal.style.cursor = "zoom-out";

    const img = document.createElement("img");
    img.src = e.target.src;
    img.style.maxWidth = "90%";
    img.style.maxHeight = "90%";

    modal.appendChild(img);
    document.body.appendChild(modal);

    modal.addEventListener("click", () => modal.remove());
  }
});

// Fontanero Virtual
const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const resetBtn = document.getElementById("reset-chat");

let responses = {};
let responseKeysSorted = [];

function normalizeText(s) {
  if (!s) return "";
  s = s.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  s = s.replace(/[^a-zA-Z0-9\sñÑáÁéÉíÍóÓúÚüÜ\-]/g, " ");
  s = s.toLowerCase();
  s = s.replace(/\s+/g, " ").trim();
  return s;
}

fetch("json/responses.json")
  .then((res) => res.json())
  .then((data) => {
    responses = data || {};
    responseKeysSorted = Object.keys(responses)
      .map((k) => ({ key: k, n: normalizeText(k) }))
      .sort((a, b) => b.n.length - a.n.length);
  });

// Tipo máquina
function typeMessage(text, speed = 30, callback) {
  let i = 0;
  const interval = setInterval(() => {
    if (i < text.length) {
      chatBox.innerHTML += text.charAt(i);
      chatBox.scrollTop = chatBox.scrollHeight;
      i++;
    } else {
      clearInterval(interval);
      if (callback) callback();
    }
  }, speed);
}

function initWelcomeMessage() {
  if (chatBox.innerHTML.trim() === "") {
    typeMessage(
      "Hola, soy tu Fontanero Virtual 👷‍♂️. Pregúntame lo que quieras sobre fontanería y te ayudaré a encontrar la mejor solución.",
      30
    );
  }
}

resetBtn.addEventListener("click", () => {
  chatBox.innerHTML = "";
  initWelcomeMessage();
});

function ensureWhatsAppNote(text) {
  if (!text) return text;
  const lower = text.toLowerCase();
  if (
    lower.includes("whatsapp") ||
    lower.includes("enví") ||
    lower.includes("presup") ||
    lower.includes("foto") ||
    lower.includes("cotiz")
  )
    return text;
  return (
    text + " — Para una valoración y presupuesto exacto, envíame una foto por WhatsApp 📸"
  );
}

const naughtyRoots = [
  "comem",
  "comeme",
  "coméme",
  "cómem",
  "cómeme",
  "culo",
  "teta",
  "sexo",
];

function isNaughty(normalized) {
  for (const r of naughtyRoots) if (normalized.includes(r)) return true;
  return false;
}

function findResponseFor(msg) {
  const nmsg = normalizeText(msg);
  if (!nmsg) return null;

  if (isNaughty(nmsg))
    return {
      pasos: [
        "Prefiero mantener las conversaciones profesionales. Para presupuesto o asistencia, envía una foto por WhatsApp.",
      ],
    };

  for (const item of responseKeysSorted) {
    if (!item.n) continue;

    if (nmsg.includes(item.n)) return responses[item.key];

    const keyWords = item.n.split(" ").filter(Boolean);
    if (keyWords.length > 1) {
      let matchAll = true;
      for (const w of keyWords)
        if (!nmsg.includes(w)) {
          matchAll = false;
          break;
        }
      if (matchAll) return responses[item.key];
    }
  }

  return null;
}

function getAnswerText(msg) {
  const res = findResponseFor(msg);
  if (res) {
    let text = "";

    if (res.pasos && Array.isArray(res.pasos))
      text = res.pasos.join(" | ");
    else if (res.steps && Array.isArray(res.steps))
      text = res.steps.join(" | ");
    else if (typeof res === "string") text = res;
    else text = JSON.stringify(res);

    return ensureWhatsAppNote(text);
  }

  return "Lo siento, no entiendo la pregunta con precisión. Para ayudarte mejor, envíame una foto por WhatsApp 📸";
}

function appendUser(msg) {
  const d = document.createElement("div");
  d.className = "message-user";
  d.innerHTML = `<strong>Tú:</strong> ${escapeHtml(msg)}`;
  chatBox.appendChild(d);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function appendBot(msg) {
  const d = document.createElement("div");
  d.className = "message-bot";
  d.innerHTML = `<strong>Fontanero:</strong> ${escapeHtml(msg)}`;
  chatBox.appendChild(d);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

sendBtn.addEventListener("click", () => {
  const msg = userInput.value.trim();
  if (!msg) return;

  appendUser(msg);
  userInput.value = "";

  setTimeout(() => {
    appendBot(getAnswerText(msg));
  }, 250);
});

userInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendBtn.click();
});
