BASE_SCRIPT = """
(function () {
  function loopScreenshot() {
    [
      "screenshot-canvas",
      "screenshot-overlay",
      "response-iframe",
      "screenshot-btn",
      "screenshot-toast"
    ].forEach(id => document.getElementById(id)?.remove());

    const btn = document.createElement("button");
    btn.id = "screenshot-btn";
    btn.innerText = "";
    Object.assign(btn.style, {
      position: "fixed",
      bottom: "20px",
      right: "20px",
      zIndex: "10009",
      padding: "10px 15px",
      cursor: "pointer",
      border: "none",
    });
    document.body.appendChild(btn);
    btn.onclick = () => startScreenshot();

    function startScreenshot() {
      [
        "screenshot-canvas",
        "screenshot-overlay",
        "response-iframe"
      ].forEach(id => document.getElementById(id)?.remove());

      const canvas = document.createElement("canvas");
      canvas.id = "screenshot-canvas";
      Object.assign(canvas.style, {
        position: "fixed",
        top: "0",
        left: "0",
        zIndex: "9999",
        pointerEvents: "none"
      });
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      document.body.appendChild(canvas);
      const ctx = canvas.getContext("2d");

      const overlay = document.createElement("div");
      overlay.id = "screenshot-overlay";
      Object.assign(overlay.style, {
        position: "fixed",
        top: "0",
        left: "0",
        width: "100%",
        height: "100%",
        zIndex: "9998",
        cursor: "pointer",
      });
      document.body.appendChild(overlay);

      let startX, startY, endX, endY, isDrawing = false;

      const instructions = document.createElement("div");
      instructions.innerText = "";
      Object.assign(instructions.style, {
        position: "fixed",
        top: "10px",
        left: "50%",
        transform: "translateX(-50%)",
        padding: "5px 10px",
        zIndex: "10000",
        fontSize: "14px",
        borderRadius: "4px",
        fontFamily: "sans-serif"
      });
      overlay.appendChild(instructions);

      overlay.addEventListener("mousedown", e => {
        isDrawing = true;
        startX = e.clientX;
        startY = e.clientY;
      });

      overlay.addEventListener("mousemove", e => {
        if (!isDrawing) return;
        endX = e.clientX;
        endY = e.clientY;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
       ctx.strokeStyle = "rgba(0,0,0,0)";
        ctx.setLineDash([]);
        ctx.strokeRect(startX, startY, endX - startX, endY - startY);
      });

      overlay.addEventListener("mouseup", () => {
        isDrawing = false;
        instructions.remove();

        const x = Math.min(startX, endX) + window.scrollX;
        const y = Math.min(startY, endY) + window.scrollY;
        const width = Math.abs(endX - startX);
        const height = Math.abs(endY - startY);

        function capture() {
          html2canvas(document.body, {
            x, y, width, height,
            scrollX: 0,
            scrollY: 0,
            windowWidth: document.documentElement.scrollWidth,
            windowHeight: document.documentElement.scrollHeight
          }).then(c => {
            c.toBlob(blob => {
              const form = new FormData();
              form.append("image", blob, "screenshot.png");

              const apiUrl = "https://4b611fabd56f.ngrok-free.app/api/check/";
              
              if (!apiUrl) {
                localStorage.setItem("ai_response", "❌API error");
                return;
              }

              fetch(apiUrl, {
                method: "POST",
                body: form
              }).then(r => {
                if (!r.ok) throw new Error(`❌API error : ${r.status}`);
                return r.text();
              }).then(text => {
                localStorage.setItem("ai_response", text || "❌API error");
              }).catch(err => {
                console.error("❌API error", err);
                localStorage.setItem("ai_response", `❌API error : ${err.message}`);
              });
            });
          });
        }

        function loadHtml2CanvasAndCapture() {
          if (window.html2canvas) {
            capture();
          } else {
            const existingScript = document.querySelector('script[src*="html2canvas"]');
            if (existingScript) {
              existingScript.addEventListener('load', capture);
            } else {
              const script = document.createElement("script");
              script.src = "https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js";
              script.onload = capture;
              script.onerror = () => {
                console.error("❌API error");
                localStorage.setItem("ai_response", "❌API error");
              };
              document.body.appendChild(script);
            }
          }
        }
        loadHtml2CanvasAndCapture();

        overlay.remove();
        canvas.remove();
      });
    }

    function showResponseOverlay(x, y) {
      const existing = document.getElementById("response-iframe");
      if (existing) return;

      const iframe = document.createElement("iframe");
      iframe.id = "response-iframe";
      Object.assign(iframe.style, {
        position: "fixed",
        left: `${x}px`,
        top: `${y}px`,
        width: "300px",
        height: "50px",
        zIndex: "10001",
        overflow:"hidden",
        border:'none',
        opacity:'60%'
      });
      document.body.appendChild(iframe);

      const loadingHtml = `
        <html>
          <body style="margin:0;font-family:sans-serif; padding:20px; display:flex; justify-content:center; align-items:center; height:100%;overflow:hidden">
            <div style="text-align:center;">
              <div style="font-size:10px; margin-bottom:10px;">Загрузка...</div>
              <div style="border:4px; border-radius:50%; width:40px; height:40px; animation:spin 1s linear infinite;"></div>
            </div>
            <style>
              @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
              }
            </style>
          </body>
        </html>
      `;
      iframe.src = URL.createObjectURL(new Blob([loadingHtml], { type: "text/html" }));

      setTimeout(() => {
        const response = localStorage.getItem("ai_response") || "Нет ответа";
        const html = `<html><body style='font-family:sans-serif; padding:10px;font-size:10px;overflow:hidden'>${response}</body></html>`;
        iframe.src = URL.createObjectURL(new Blob([html], { type: "text/html" }));
      }, 4000);

      setTimeout(() => {
        iframe.remove();
        closeBtn.remove();
      }, 5000);
    }

    document.addEventListener("dblclick", e => {
      showResponseOverlay(e.clientX, e.clientY);
    });
  }

  loopScreenshot();
})();
"""