(function() {
    "use strict";

    let xmlFiles = [];
    let pngFiles = [];
    let outputFolder = null;
    let isProcessing = false;

    const xmlListContainer = document.getElementById('xmlListContainer');
    const pngListContainer = document.getElementById('pngListContainer');
    const outputFolderLabel = document.getElementById('outputFolderLabel');
    const statusText = document.getElementById('statusText');
    const processBtn = document.getElementById('processBtn');
    const aaCheckbox = document.getElementById('aaCheckbox');

    function escapeHtml(str) {
        return String(str).replace(/[&<>"]/g, function(m) {
            if (m === '&') return '&amp;';
            if (m === '<') return '&lt;';
            if (m === '>') return '&gt;';
            if (m === '"') return '&quot;';
            return m;
        });
    }

    function renderLists() {
        if (xmlFiles.length === 0) {
            xmlListContainer.innerHTML = `<div class="list-empty">No XML files loaded</div>`;
        } else {
            xmlListContainer.innerHTML = xmlFiles.map(f => 
                `<div class="list-item"><span style="margin-right:8px;color:#4FC3F7;">📄</span>${escapeHtml(f.name)}</div>`
            ).join('');
        }

        if (pngFiles.length === 0) {
            pngListContainer.innerHTML = `<div class="list-empty">No images loaded</div>`;
        } else {
            pngListContainer.innerHTML = pngFiles.map(f => 
                `<div class="list-item"><span style="margin-right:8px;color:#4FC3F7;">🖼️</span>${escapeHtml(f.name)}</div>`
            ).join('');
        }
        updateStatus('files');
    }

    function updateStatus(type, msg) {
        if (type === 'files') {
            const total = xmlFiles.length + pngFiles.length;
            if (total === 0) statusText.textContent = 'Ready';
            else if (xmlFiles.length > 1 || pngFiles.length > 1) {
                statusText.textContent = `Batch mode: ${xmlFiles.length} XML, ${pngFiles.length} PNG files loaded`;
            } else if (xmlFiles.length === 1 && pngFiles.length === 1) {
                statusText.textContent = 'Single mode: 1 XML, 1 PNG file loaded';
            } else {
                statusText.textContent = `Loaded ${xmlFiles.length} XML, ${pngFiles.length} PNG`;
            }
        } else if (type === 'info') {
            statusText.textContent = msg || 'Ready';
        } else if (type === 'error') {
            statusText.textContent = msg || 'Error';
        } else {
            statusText.textContent = msg || 'Ready';
        }
    }

    document.getElementById('loadXmlBtn').addEventListener('click', () => {
        const input = document.createElement('input');
        input.type = 'file';
        input.multiple = true;
        input.accept = '.xml';
        input.onchange = (e) => {
            const files = Array.from(e.target.files);
            if (files.length === 0) return;
            xmlFiles = files.map(f => ({ name: f.name, file: f }));
            renderLists();
        };
        input.click();
    });

    document.getElementById('loadPngBtn').addEventListener('click', () => {
        const input = document.createElement('input');
        input.type = 'file';
        input.multiple = true;
        input.accept = '.png';
        input.onchange = (e) => {
            const files = Array.from(e.target.files);
            if (files.length === 0) return;
            pngFiles = files.map(f => ({ name: f.name, file: f }));
            renderLists();
        };
        input.click();
    });

    document.getElementById('selectOutputBtn').addEventListener('click', async () => {
        if (window.showDirectoryPicker) {
            try {
                const dir = await window.showDirectoryPicker();
                outputFolder = dir;
                outputFolderLabel.textContent = dir.name;
                updateStatus('info', `Output folder: ${dir.name}`);
            } catch (err) {
                if (err.name !== 'AbortError') {
                    alert('Could not select folder: ' + err.message);
                }
            }
        } else {
            const folderName = prompt('Enter output folder name (will be created in memory):', 'optimized_output');
            if (folderName && folderName.trim()) {
                outputFolder = { name: folderName.trim(), _fallback: true };
                outputFolderLabel.textContent = folderName.trim();
                updateStatus('info', `Output folder: ${folderName.trim()}`);
            } else {
                updateStatus('info', 'Output folder not set');
            }
        }
    });

    function smartDivide(value, attr, division) {
        if (value === undefined || value === null) return value;
        try {
            const num = parseFloat(value);
            if (isNaN(num)) return value;
            let result = num / division;
            if (['x', 'y', 'frameX', 'frameY'].includes(attr)) {
                result = Math.round(result * 2) / 2;
                return Number.isInteger(result) ? String(Math.round(result)) : String(result);
            } else {
                result = Math.round(result);
                result = Math.max(1, result);
                return String(Math.round(result));
            }
        } catch (e) {
            return value;
        }
    }

    function processXMLText(xmlText, division) {
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(xmlText, 'text/xml');
        const parserError = xmlDoc.querySelector('parsererror');
        if (parserError) {
            throw new Error('Invalid XML: ' + parserError.textContent);
        }
        const subTextures = xmlDoc.getElementsByTagName('SubTexture');
        for (let el of subTextures) {
            const attrs = ['x', 'y', 'width', 'height', 'frameX', 'frameY', 'frameWidth', 'frameHeight'];
            for (let attr of attrs) {
                const val = el.getAttribute(attr);
                if (val !== null) {
                    const newVal = smartDivide(val, attr, division);
                    el.setAttribute(attr, newVal);
                }
            }
        }
        const serializer = new XMLSerializer();
        let result = serializer.serializeToString(xmlDoc);
        if (!result.startsWith('<?xml')) {
            result = '<?xml version="1.0" encoding="UTF-8"?>\n' + result;
        }
        return result;
    }

    function resizePNG(imageData, width, height, targetWidth, targetHeight, useAA) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => {
                const canvas = document.createElement('canvas');
                canvas.width = targetWidth;
                canvas.height = targetHeight;
                const ctx = canvas.getContext('2d');
                if (useAA) {
                    ctx.imageSmoothingEnabled = true;
                    ctx.imageSmoothingQuality = 'high';
                } else {
                    ctx.imageSmoothingEnabled = false;
                    ctx.imageSmoothingQuality = 'low';
                }
                ctx.drawImage(img, 0, 0, targetWidth, targetHeight);
                canvas.toBlob((blob) => {
                    if (blob) {
                        resolve(blob);
                    } else {
                        reject(new Error('Failed to create PNG blob'));
                    }
                }, 'image/png');
            };
            img.onerror = () => reject(new Error('Failed to load image'));
            img.src = URL.createObjectURL(new Blob([imageData], { type: 'image/png' }));
        });
    }

    function loadImageFromBlob(blob) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => resolve(img);
            img.onerror = () => reject(new Error('Failed to load image for size detection'));
            img.src = URL.createObjectURL(blob);
        });
    }

    async function saveFile(data, fileName, mimeType) {
        if (outputFolder && typeof outputFolder === 'object' && 'getFileHandle' in outputFolder) {
            try {
                const fileHandle = await outputFolder.getFileHandle(fileName, { create: true });
                const writable = await fileHandle.createWritable();
                let blob;
                if (typeof data === 'string') {
                    blob = new Blob([data], { type: mimeType });
                } else if (data instanceof Blob) {
                    blob = data;
                } else {
                    blob = new Blob([data], { type: mimeType });
                }
                await writable.write(blob);
                await writable.close();
                return;
            } catch (e) {
                console.warn('FileSystem API write failed, falling back to download', e);
            }
        }

        let blob;
        if (typeof data === 'string') {
            blob = new Blob([data], { type: mimeType });
        } else if (data instanceof Blob) {
            blob = data;
        } else {
            blob = new Blob([data], { type: mimeType });
        }
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
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
            alert('Please load XML and/or PNG files first!');
            updateStatus('error', 'No files loaded');
            return;
        }
        if (!outputFolder) {
            alert('Please select an output folder first!');
            updateStatus('error', 'No output folder');
            return;
        }

        isProcessing = true;
        processBtn.disabled = true;
        processBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        updateStatus('info', 'Processing started...');

        const division = 2;
        const useAA = aaCheckbox.checked;
        let xmlProcessed = 0;
        let pngProcessed = 0;
        let errorOccurred = false;
        const errors = [];

        try {
            for (let i = 0; i < xmlFiles.length; i++) {
                updateStatus('info', `Processing XML ${i+1}/${xmlFiles.length}: ${xmlFiles[i].name}`);
                try {
                    const text = await xmlFiles[i].file.text();
                    const processed = processXMLText(text, division);
                    await saveFile(processed, xmlFiles[i].name, 'application/xml');
                    xmlProcessed++;
                } catch (e) {
                    errors.push(`XML ${xmlFiles[i].name}: ${e.message}`);
                    errorOccurred = true;
                }
            }

            for (let i = 0; i < pngFiles.length; i++) {
                updateStatus('info', `Processing image ${i+1}/${pngFiles.length}: ${pngFiles[i].name}`);
                try {
                    const arrayBuffer = await pngFiles[i].file.arrayBuffer();
                    const blob = new Blob([arrayBuffer], { type: 'image/png' });
                    const img = await loadImageFromBlob(blob);
                    const originalWidth = img.width;
                    const originalHeight = img.height;
                    const newWidth = Math.max(1, Math.round(originalWidth / division));
                    const newHeight = Math.max(1, Math.round(originalHeight / division));

                    const resizedBlob = await resizePNG(arrayBuffer, originalWidth, originalHeight, newWidth, newHeight, useAA);
                    await saveFile(resizedBlob, pngFiles[i].name, 'image/png');
                    pngProcessed++;
                } catch (e) {
                    errors.push(`PNG ${pngFiles[i].name}: ${e.message}`);
                    errorOccurred = true;
                }
            }

            let msg = `Completed! Processed ${xmlProcessed} XML file(s) and ${pngProcessed} image(s).`;
            if (errors.length > 0) {
                msg += `\nErrors: ${errors.join('; ')}`;
            }
            if (!errorOccurred) {
                alert('Processing Complete!\n' + msg);
            } else {
                alert('Processing completed with errors.\n' + msg);
            }
            updateStatus('info', msg);
        } catch (err) {
            alert('Processing Error: ' + err.message);
            updateStatus('error', err.message);
        } finally {
            isProcessing = false;
            processBtn.disabled = false;
            processBtn.innerHTML = '<i class="fas fa-play"></i> Modify and Resize';
        }
    }

    document.getElementById('processBtn').addEventListener('click', processFiles);

    renderLists();
})();