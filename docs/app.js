(function () {
  "use strict";

  let xmlFiles = [];
  let pngFiles = [];
  let outputFolder = null;
  let isProcessing = false;

  const xmlListContainer = document.getElementById("xmlListContainer");
  const pngListContainer = document.getElementById("pngListContainer");
  const outputFolderLabel = document.getElementById("outputFolderLabel");
  const statusText = document.getElementById("statusText");
  const processBtn = document.getElementById("processBtn");
  const aaCheckbox = document.getElementById("aaCheckbox");
  const clearAllBtn = document.getElementById("clearAllBtn");

  function escapeHtml(str) {
    return String(str).replace(/[&<>"]/g, (m) => {
      if (m === "&") return "&amp;";
      if (m === "<") return "&lt;";
      if (m === ">") return "&gt;";
      if (m === '"') return "&quot;";
      return m;
    });
  }

  function renderLists() {
    if (xmlFiles.length === 0) {
      xmlListContainer.innerHTML = `<div class="list-empty">No XML loaded</div>`;
    } else {
      xmlListContainer.innerHTML = xmlFiles
        .map(
          (f, index) =>
            `<div class="list-item" data-index="${index}" data-type="xml">
          <span class="material-symbols-outlined">description</span>
          <span class="file-name">${escapeHtml(f.name)}</span>
          <button class="remove-btn" data-index="${index}" data-type="xml" title="Remove file">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>`,
        )
        .join("");

      document
        .querySelectorAll("#xmlListContainer .remove-btn")
        .forEach((btn) => {
          btn.addEventListener("click", (e) => {
            e.stopPropagation();
            const index = parseInt(btn.dataset.index);
            removeFile("xml", index);
          });
        });
    }

    if (pngFiles.length === 0) {
      pngListContainer.innerHTML = `<div class="list-empty">No images loaded</div>`;
    } else {
      pngListContainer.innerHTML = pngFiles
        .map(
          (f, index) =>
            `<div class="list-item" data-index="${index}" data-type="png">
          <span class="material-symbols-outlined">image</span>
          <span class="file-name">${escapeHtml(f.name)}</span>
          <button class="remove-btn" data-index="${index}" data-type="png" title="Remove file">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>`,
        )
        .join("");

      document
        .querySelectorAll("#pngListContainer .remove-btn")
        .forEach((btn) => {
          btn.addEventListener("click", (e) => {
            e.stopPropagation();
            const index = parseInt(btn.dataset.index);
            removeFile("png", index);
          });
        });
    }

    updateClearAllButton();
    updateStatus("files");
  }

  function removeFile(type, index) {
    if (type === "xml") {
      xmlFiles.splice(index, 1);
    } else if (type === "png") {
      pngFiles.splice(index, 1);
    }
    renderLists();
  }

  function clearAllFiles() {
    if (xmlFiles.length === 0 && pngFiles.length === 0) return;

    const confirmed = confirm("Are you sure you want to remove all files?");
    if (confirmed) {
      xmlFiles = [];
      pngFiles = [];
      renderLists();
      updateStatus("info", "All files cleared");
    }
  }

  function updateClearAllButton() {
    const total = xmlFiles.length + pngFiles.length;
    if (total > 0) {
      clearAllBtn.style.display = "flex";
      clearAllBtn.textContent = `Clear All (${total})`;
    } else {
      clearAllBtn.style.display = "none";
    }
  }

  function updateStatus(type, msg) {
    if (type === "files") {
      const total = xmlFiles.length + pngFiles.length;
      if (total === 0) statusText.textContent = "Ready";
      else if (xmlFiles.length > 1 || pngFiles.length > 1) {
        statusText.textContent = `Batch: ${xmlFiles.length} XML, ${pngFiles.length} PNG`;
      } else if (xmlFiles.length === 1 && pngFiles.length === 1) {
        statusText.textContent = "Single: 1 XML, 1 PNG";
      } else {
        statusText.textContent = `Loaded ${xmlFiles.length} XML, ${pngFiles.length} PNG`;
      }
    } else if (type === "info") {
      statusText.textContent = msg || "Ready";
    } else {
      statusText.textContent = msg || "Ready";
    }
  }

  function handleFiles(files, type) {
    const validFiles = Array.from(files).filter((f) => {
      if (type === "xml") return f.name.toLowerCase().endsWith(".xml");
      if (type === "png") return f.name.toLowerCase().endsWith(".png");
      return false;
    });

    if (validFiles.length === 0) {
      return false;
    }

    if (type === "xml") {
      xmlFiles = validFiles.map((f) => ({ name: f.name, file: f }));
    } else if (type === "png") {
      pngFiles = validFiles.map((f) => ({ name: f.name, file: f }));
    }
    renderLists();
    return true;
  }

  function handleFolderFiles(files) {
    const xmlFilesFound = [];
    const pngFilesFound = [];

    for (const file of files) {
      if (file.name.toLowerCase().endsWith(".xml")) {
        xmlFilesFound.push(file);
      } else if (file.name.toLowerCase().endsWith(".png")) {
        pngFilesFound.push(file);
      }
    }

    let hasFiles = false;

    if (xmlFilesFound.length > 0) {
      xmlFiles = xmlFilesFound.map((f) => ({ name: f.name, file: f }));
      hasFiles = true;
    }

    if (pngFilesFound.length > 0) {
      pngFiles = pngFilesFound.map((f) => ({ name: f.name, file: f }));
      hasFiles = true;
    }

    if (hasFiles) {
      renderLists();
      updateStatus(
        "info",
        `Loaded ${xmlFiles.length} XML and ${pngFiles.length} PNG from folder`,
      );
      return true;
    }

    return false;
  }

  function setupDragAndDrop() {
    const dropZones = document.querySelectorAll(".drop-zone");

    dropZones.forEach((zone) => {
      ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
        zone.addEventListener(eventName, (e) => {
          e.preventDefault();
          e.stopPropagation();
        });
      });

      ["dragenter", "dragover"].forEach((eventName) => {
        zone.addEventListener(eventName, () => {
          zone.classList.add("drag-over");
        });
      });

      ["dragleave", "drop"].forEach((eventName) => {
        zone.addEventListener(eventName, () => {
          zone.classList.remove("drag-over");
        });
      });

      zone.addEventListener("drop", (e) => {
        const items = e.dataTransfer.items;
        const files = [];

        let isFolder = false;
        for (let i = 0; i < items.length; i++) {
          const item = items[i];
          if (item.kind === "file") {
            const entry = item.webkitGetAsEntry
              ? item.webkitGetAsEntry()
              : null;
            if (entry && entry.isDirectory) {
              isFolder = true;
              break;
            }
          }
        }

        if (isFolder) {
          const entries = [];
          for (let i = 0; i < items.length; i++) {
            const entry = items[i].webkitGetAsEntry
              ? items[i].webkitGetAsEntry()
              : null;
            if (entry) {
              entries.push(entry);
            }
          }

          const allFiles = [];
          const processEntry = (entry) => {
            return new Promise((resolve) => {
              if (entry.isFile) {
                entry.file((file) => {
                  allFiles.push(file);
                  resolve();
                });
              } else if (entry.isDirectory) {
                const reader = entry.createReader();
                const readEntries = () => {
                  reader.readEntries((entries) => {
                    if (entries.length === 0) {
                      resolve();
                    } else {
                      Promise.all(entries.map(processEntry)).then(readEntries);
                    }
                  });
                };
                readEntries();
              } else {
                resolve();
              }
            });
          };

          Promise.all(entries.map(processEntry)).then(() => {
            if (allFiles.length > 0) {
              handleFolderFiles(allFiles);
            }
          });
        } else {
          const files = e.dataTransfer.files;
          const type = zone.dataset.type;
          handleFiles(files, type);
        }
      });
    });

    document.addEventListener("dragover", (e) => {
      e.preventDefault();
    });

    document.addEventListener("drop", (e) => {
      e.preventDefault();
      const items = e.dataTransfer.items;

      let isFolder = false;
      for (let i = 0; i < items.length; i++) {
        const item = items[i];
        if (item.kind === "file") {
          const entry = item.webkitGetAsEntry ? item.webkitGetAsEntry() : null;
          if (entry && entry.isDirectory) {
            isFolder = true;
            break;
          }
        }
      }

      if (isFolder) {
        const entries = [];
        for (let i = 0; i < items.length; i++) {
          const entry = items[i].webkitGetAsEntry
            ? items[i].webkitGetAsEntry()
            : null;
          if (entry) {
            entries.push(entry);
          }
        }

        const allFiles = [];
        const processEntry = (entry) => {
          return new Promise((resolve) => {
            if (entry.isFile) {
              entry.file((file) => {
                allFiles.push(file);
                resolve();
              });
            } else if (entry.isDirectory) {
              const reader = entry.createReader();
              const readEntries = () => {
                reader.readEntries((entries) => {
                  if (entries.length === 0) {
                    resolve();
                  } else {
                    Promise.all(entries.map(processEntry)).then(readEntries);
                  }
                });
              };
              readEntries();
            } else {
              resolve();
            }
          });
        };

        Promise.all(entries.map(processEntry)).then(() => {
          if (allFiles.length > 0) {
            handleFolderFiles(allFiles);
          }
        });
      } else {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
          const hasXml = Array.from(files).some((f) =>
            f.name.toLowerCase().endsWith(".xml"),
          );
          const hasPng = Array.from(files).some((f) =>
            f.name.toLowerCase().endsWith(".png"),
          );

          let loaded = false;
          if (hasXml) {
            const xmlFilesDropped = Array.from(files).filter((f) =>
              f.name.toLowerCase().endsWith(".xml"),
            );
            if (xmlFilesDropped.length > 0) {
              loaded = handleFiles(xmlFilesDropped, "xml");
            }
          }
          if (hasPng) {
            const pngFilesDropped = Array.from(files).filter((f) =>
              f.name.toLowerCase().endsWith(".png"),
            );
            if (pngFilesDropped.length > 0) {
              loaded = handleFiles(pngFilesDropped, "png");
            }
          }
          if (!loaded) {
            updateStatus("info", "No valid XML or PNG files found");
          }
        }
      }
    });
  }

  document.getElementById("loadXmlBtn").addEventListener("click", () => {
    const input = document.createElement("input");
    input.type = "file";
    input.multiple = true;
    input.accept = ".xml";
    input.webkitdirectory = false;
    input.onchange = (e) => {
      const files = Array.from(e.target.files);
      if (files.length === 0) return;
      handleFiles(files, "xml");
    };
    input.click();
  });

  document.getElementById("loadPngBtn").addEventListener("click", () => {
    const input = document.createElement("input");
    input.type = "file";
    input.multiple = true;
    input.accept = ".png";
    input.webkitdirectory = false;
    input.onchange = (e) => {
      const files = Array.from(e.target.files);
      if (files.length === 0) return;
      handleFiles(files, "png");
    };
    input.click();
  });

  clearAllBtn.addEventListener("click", clearAllFiles);

  document
    .getElementById("selectOutputBtn")
    .addEventListener("click", async () => {
      if (window.showDirectoryPicker) {
        try {
          const dir = await window.showDirectoryPicker();
          outputFolder = dir;
          outputFolderLabel.textContent = dir.name;
          updateStatus("info", `Output: ${dir.name}`);
        } catch (err) {
          if (err.name !== "AbortError") alert("Folder error: " + err.message);
        }
      } else {
        const folderName = prompt(
          "Enter output folder name:",
          "optimized_output",
        );
        if (folderName && folderName.trim()) {
          outputFolder = { name: folderName.trim(), _fallback: true };
          outputFolderLabel.textContent = folderName.trim();
          updateStatus("info", `Output: ${folderName.trim()}`);
        } else {
          updateStatus("info", "Output folder not set");
        }
      }
    });

  function smartDivide(value, attr, division) {
    if (value === undefined || value === null) return value;
    const num = parseFloat(value);
    if (isNaN(num)) return value;
    let result = num / division;
    if (["x", "y", "frameX", "frameY"].includes(attr)) {
      result = Math.round(result * 2) / 2;
      return Number.isInteger(result)
        ? String(Math.round(result))
        : String(result);
    } else {
      result = Math.round(result);
      result = Math.max(1, result);
      return String(Math.round(result));
    }
  }

  function processXMLText(xmlText, division) {
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(xmlText, "text/xml");
    const parserError = xmlDoc.querySelector("parsererror");
    if (parserError) throw new Error("Invalid XML: " + parserError.textContent);
    const subTextures = xmlDoc.getElementsByTagName("SubTexture");
    for (let el of subTextures) {
      [
        "x",
        "y",
        "width",
        "height",
        "frameX",
        "frameY",
        "frameWidth",
        "frameHeight",
      ].forEach((attr) => {
        const val = el.getAttribute(attr);
        if (val !== null) {
          el.setAttribute(attr, smartDivide(val, attr, division));
        }
      });
    }
    const serializer = new XMLSerializer();
    let result = serializer.serializeToString(xmlDoc);
    if (!result.startsWith("<?xml"))
      result = '<?xml version="1.0" encoding="UTF-8"?>\n' + result;
    return result;
  }

  function resizePNG(
    imageData,
    width,
    height,
    targetWidth,
    targetHeight,
    useAA,
  ) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement("canvas");
        canvas.width = targetWidth;
        canvas.height = targetHeight;
        const ctx = canvas.getContext("2d");
        ctx.imageSmoothingEnabled = useAA;
        ctx.imageSmoothingQuality = useAA ? "high" : "low";
        ctx.drawImage(img, 0, 0, targetWidth, targetHeight);
        canvas.toBlob(
          (blob) => (blob ? resolve(blob) : reject(new Error("blob failed"))),
          "image/png",
        );
      };
      img.onerror = () => reject(new Error("load image failed"));
      img.src = URL.createObjectURL(
        new Blob([imageData], { type: "image/png" }),
      );
    });
  }

  function loadImageFromBlob(blob) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve(img);
      img.onerror = () => reject(new Error("image size detection failed"));
      img.src = URL.createObjectURL(blob);
    });
  }

  async function createZipBlob(files) {
    return new Promise((resolve, reject) => {
      if (typeof JSZip === "undefined") {
        const script = document.createElement("script");
        script.src =
          "https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js";
        script.onload = () => {
          createZipWithJSZip(files).then(resolve).catch(reject);
        };
        script.onerror = () => {
          reject(
            new Error(
              "Failed to load JSZip library. Please check your internet connection.",
            ),
          );
        };
        document.head.appendChild(script);
      } else {
        createZipWithJSZip(files).then(resolve).catch(reject);
      }
    });
  }

  async function createZipWithJSZip(files) {
    const zip = new JSZip();

    for (const file of files) {
      const data = file.data;
      const name = file.name;

      if (typeof data === "string") {
        zip.file(name, data);
      } else if (data instanceof Blob) {
        zip.file(name, data);
      } else if (data instanceof ArrayBuffer) {
        zip.file(name, data);
      }
    }

    return await zip.generateAsync({
      type: "blob",
      compression: "DEFLATE",
      compressionOptions: {
        level: 6,
      },
    });
  }

  async function saveZipFile(blob, fileName) {
    if (
      outputFolder &&
      typeof outputFolder === "object" &&
      "getFileHandle" in outputFolder
    ) {
      try {
        const fileHandle = await outputFolder.getFileHandle(fileName, {
          create: true,
        });
        const writable = await fileHandle.createWritable();
        await writable.write(blob);
        await writable.close();
        return;
      } catch (e) {
        console.warn("FS fallback", e);
      }
    }

    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 5000);
  }

  async function saveFile(data, fileName, mimeType) {
    if (
      outputFolder &&
      typeof outputFolder === "object" &&
      "getFileHandle" in outputFolder
    ) {
      try {
        const fileHandle = await outputFolder.getFileHandle(fileName, {
          create: true,
        });
        const writable = await fileHandle.createWritable();
        const blob =
          typeof data === "string"
            ? new Blob([data], { type: mimeType })
            : data instanceof Blob
              ? data
              : new Blob([data], { type: mimeType });
        await writable.write(blob);
        await writable.close();
        return;
      } catch (e) {
        console.warn("FS fallback", e);
      }
    }
    const blob =
      typeof data === "string"
        ? new Blob([data], { type: mimeType })
        : data instanceof Blob
          ? data
          : new Blob([data], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 5000);
  }

  async function processFiles() {
    if (isProcessing) return;
    if (xmlFiles.length === 0 && pngFiles.length === 0) {
      alert("Please load XML and/or PNG files.");
      updateStatus("error", "No files");
      return;
    }
    if (!outputFolder) {
      alert("Select an output folder first.");
      updateStatus("error", "No output folder");
      return;
    }

    isProcessing = true;
    processBtn.disabled = true;
    processBtn.innerHTML = `<span class="material-symbols-outlined" style="animation:spin 1s linear infinite;">progress_activity</span> Processing...`;
    updateStatus("info", "Processing started...");

    const division = 2;
    const useAA = aaCheckbox.checked;
    let xmlProcessed = 0,
      pngProcessed = 0,
      errors = [];
    const processedFiles = [];
    const isBatch = xmlFiles.length > 1 || pngFiles.length > 1;

    try {
      for (let i = 0; i < xmlFiles.length; i++) {
        updateStatus(
          "info",
          `XML ${i + 1}/${xmlFiles.length}: ${xmlFiles[i].name}`,
        );
        try {
          const text = await xmlFiles[i].file.text();
          const processed = processXMLText(text, division);
          const fileName = xmlFiles[i].name;

          if (isBatch) {
            processedFiles.push({ name: fileName, data: processed });
          } else {
            await saveFile(processed, fileName, "application/xml");
          }
          xmlProcessed++;
        } catch (e) {
          errors.push(`XML ${xmlFiles[i].name}: ${e.message}`);
        }
      }

      for (let i = 0; i < pngFiles.length; i++) {
        updateStatus(
          "info",
          `Image ${i + 1}/${pngFiles.length}: ${pngFiles[i].name}`,
        );
        try {
          const arrayBuffer = await pngFiles[i].file.arrayBuffer();
          const blob = new Blob([arrayBuffer], { type: "image/png" });
          const img = await loadImageFromBlob(blob);
          const newWidth = Math.max(1, Math.round(img.width / division));
          const newHeight = Math.max(1, Math.round(img.height / division));
          const resized = await resizePNG(
            arrayBuffer,
            img.width,
            img.height,
            newWidth,
            newHeight,
            useAA,
          );
          const fileName = pngFiles[i].name;

          if (isBatch) {
            processedFiles.push({ name: fileName, data: resized });
          } else {
            await saveFile(resized, fileName, "image/png");
          }
          pngProcessed++;
        } catch (e) {
          errors.push(`PNG ${pngFiles[i].name}: ${e.message}`);
        }
      }

      if (isBatch && processedFiles.length > 0) {
        updateStatus("info", "Creating ZIP archive...");
        try {
          const zipBlob = await createZipBlob(processedFiles);
          await saveZipFile(zipBlob, "optimized_characters.zip");
          updateStatus("info", "ZIP archive created successfully");
        } catch (e) {
          errors.push(`ZIP creation: ${e.message}`);
        }
      }

      let msg = `Done: ${xmlProcessed} XML, ${pngProcessed} PNG.`;
      if (isBatch) {
        msg += ` ZIP archive created with ${processedFiles.length} files.`;
      }
      if (errors.length) msg += ` Errors: ${errors.join("; ")}`;
      alert(
        errors.length ? "Completed with errors.\n" + msg : "Complete!\n" + msg,
      );
      updateStatus("info", msg);
    } catch (err) {
      alert("Error: " + err.message);
      updateStatus("error", err.message);
    } finally {
      isProcessing = false;
      processBtn.disabled = false;
      processBtn.innerHTML = `<span class="material-symbols-outlined">play_arrow</span> Modify and Resize`;
    }
  }

  document.getElementById("processBtn").addEventListener("click", processFiles);

  setupDragAndDrop();
  renderLists();
})();
