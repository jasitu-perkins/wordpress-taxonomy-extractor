<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WordPress Tag Extractor</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .custom-scrollbar::-webkit-scrollbar {
            width: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
            background: #f1f1f1;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
    </style>
</head>
<body class="bg-gray-50 min-h-screen font-sans">

    <div class="max-w-7xl mx-auto py-10 px-4">
        <header class="mb-8 text-center">
            <h1 class="text-3xl font-bold text-gray-800">WordPress Tag Extractor</h1>
            <p class="text-gray-600 mt-2">Extract Tag IDs, Names, Slugs, Types, and Post Counts</p>
        </header>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <!-- Input Section -->
            <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-lg font-semibold text-gray-700">HTML Input</h2>
                    <button id="clearBtn" class="text-sm text-red-500 hover:text-red-700 font-medium">Clear All</button>
                </div>
                <textarea 
                    id="htmlInput" 
                    placeholder="Paste <table>, <tbody>, or <tr> blocks here..." 
                    class="w-full h-[550px] p-4 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none font-mono text-sm custom-scrollbar"
                ></textarea>
            </div>

            <!-- Output Section -->
            <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 flex flex-col">
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-lg font-semibold text-gray-700">Extracted Data</h2>
                    <span id="countBadge" class="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded-full">0 Items</span>
                </div>
                
                <div class="overflow-auto max-h-[450px] border border-gray-100 rounded-lg custom-scrollbar">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50">
                            <tr>
                                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Slug</th>
                                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Count</th>
                            </tr>
                        </thead>
                        <tbody id="resultsBody" class="bg-white divide-y divide-gray-200 text-sm text-gray-700">
                            <tr>
                                <td colspan="5" class="px-6 py-10 text-center text-gray-400 italic">Waiting for input...</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div class="mt-auto pt-6 space-y-3">
                    <button 
                        id="copySheetBtn" 
                        class="w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center gap-2 font-medium"
                    >
                        Copy for Google Sheets (No Header)
                    </button>
                    
                    <button 
                        id="copyListBtn" 
                        class="w-full border border-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-50 transition-colors flex items-center justify-center gap-2"
                    >
                        Copy as JSON List
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        const htmlInput = document.getElementById('htmlInput');
        const resultsBody = document.getElementById('resultsBody');
        const countBadge = document.getElementById('countBadge');
        const clearBtn = document.getElementById('clearBtn');
        const copyListBtn = document.getElementById('copyListBtn');
        const copySheetBtn = document.getElementById('copySheetBtn');

        let currentData = [];

        function extractData() {
            let html = htmlInput.value.trim();
            if (!html) {
                currentData = [];
                renderTable();
                return;
            }

            // Enhanced wrapping logic to handle <tr> OR <tbody> pastes
            if ((html.startsWith('<tr') || html.startsWith('<tbody')) && !html.includes('<table')) {
                html = `<table>${html}</table>`;
            }

            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const rows = doc.querySelectorAll('tr');
            
            currentData = [];

            rows.forEach(row => {
                const link = row.querySelector('a.row-title');
                if (!link) return;

                const name = link.textContent.replace(/^[—\s]+/, '').trim();
                const href = link.getAttribute('href') || '';
                
                try {
                    const urlObj = new URL(href, window.location.origin);
                    const tagId = urlObj.searchParams.get('tag_ID');
                    const taxonomy = urlObj.searchParams.get('taxonomy') || '';

                    if (tagId) {
                        const slugCell = row.querySelector('[data-colname="Slug"], .column-slug, .slug');
                        const slugText = slugCell ? slugCell.textContent.replace('Slug', '').trim() : 'N/A';

                        const countCell = row.querySelector('[data-colname="Count"], .column-posts, .posts');
                        let count = '0';
                        if (countCell) {
                            const countLink = countCell.querySelector('a');
                            count = (countLink ? countLink.textContent : countCell.textContent).replace('Count', '').trim();
                        }

                        const viewLink = row.querySelector('.view a');
                        const viewUrl = viewLink ? viewLink.getAttribute('href') : '#';
                        const pathType = taxonomy.replace('resource-', '') || "unknown";

                        currentData.push({ 
                            tag_id: tagId, 
                            type: pathType,
                            name: name,
                            slug: slugText,
                            url: viewUrl,
                            count: count
                        });
                    }
                } catch(e) {
                    console.error("Row parse error:", e);
                }
            });

            renderTable();
        }

        function renderTable() {
            if (currentData.length === 0) {
                resultsBody.innerHTML = `<tr><td colspan="5" class="px-6 py-10 text-center text-gray-400 italic">No valid rows detected. Make sure to paste WordPress table HTML.</td></tr>`;
                countBadge.textContent = '0 Items';
                return;
            }

            countBadge.textContent = `${currentData.length} Items`;
            resultsBody.innerHTML = currentData.map((item) => `
                <tr class="hover:bg-gray-50 transition-colors">
                    <td class="px-4 py-3 whitespace-nowrap font-mono text-blue-600 font-bold">${item.tag_id}</td>
                    <td class="px-4 py-3 whitespace-nowrap font-medium text-gray-900">${item.name}</td>
                    <td class="px-4 py-3 whitespace-nowrap font-mono text-gray-500">${item.slug}</td>
                    <td class="px-4 py-3 whitespace-nowrap">
                        <span class="px-2 py-1 rounded bg-gray-100 text-gray-600 text-[10px] uppercase font-bold">
                            ${item.type}
                        </span>
                    </td>
                    <td class="px-4 py-3 whitespace-nowrap font-mono">${item.count}</td>
                </tr>
            `).join('');
        }

        function copyToClipboard(text) {
            const el = document.createElement('textarea');
            el.value = text;
            document.body.appendChild(el);
            el.select();
            document.execCommand('copy');
            document.body.removeChild(el);
        }

        htmlInput.addEventListener('input', extractData);
        clearBtn.addEventListener('click', () => { htmlInput.value = ''; extractData(); });

        copyListBtn.addEventListener('click', () => {
            if (currentData.length === 0) return;
            copyToClipboard(JSON.stringify(currentData, null, 4));
            const btn = copyListBtn;
            const old = btn.textContent;
            btn.textContent = "Copied!";
            setTimeout(() => btn.textContent = old, 1500);
        });

        copySheetBtn.addEventListener('click', () => {
            if (currentData.length === 0) return;
            const tsv = currentData.map(item => 
                [item.tag_id, item.name, item.slug, item.type, item.count, item.url].join('\t')
            ).join('\n');
            copyToClipboard(tsv);
            const btn = copySheetBtn;
            const old = btn.textContent;
            btn.textContent = "Copied Data Rows!";
            setTimeout(() => btn.textContent = old, 1500);
        });
    </script>
</body>
</html>
