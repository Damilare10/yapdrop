document.addEventListener('DOMContentLoaded', () => {
    const tweetCountSpan = document.getElementById('tweet-count');
    const decrementBtn = document.getElementById('decrement');
    const incrementBtn = document.getElementById('increment');
    const tweetInputsContainer = document.getElementById('tweet-inputs');
    const generateBtn = document.getElementById('generate-btn');
    const resultsBody = document.getElementById('results-body');

    let count = 1;

    // --- Helpers ---

    const createInputGroup = (index, value = '') => {
        const group = document.createElement('div');
        group.className = 'input-group';
        group.innerHTML = `
            <div class="input-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                </svg>
            </div>
            <input type="text" placeholder="Tweet link ${index}..." class="tweet-input" value="${value}">
        `;
        return group;
    };

    const setCount = (n) => {
        count = n;
        tweetCountSpan.textContent = count;
    };

    // Rebuild inputs to match `count`
    const updateInputs = () => {
        const currentInputs = tweetInputsContainer.querySelectorAll('.input-group');
        const currentCount = currentInputs.length;

        if (count > currentCount) {
            for (let i = currentCount + 1; i <= count; i++) {
                tweetInputsContainer.appendChild(createInputGroup(i));
            }
        } else if (count < currentCount) {
            for (let i = currentCount; i > count; i--) {
                tweetInputsContainer.removeChild(currentInputs[i - 1]);
            }
        }
    };

    // Extract valid tweet links from arbitrary pasted text
    const extractTweetLinks = (text) => {
        const regex = /https?:\/\/(www\.)?(twitter\.com|x\.com)\/[^\s/]+\/status\/\d+[^\s]*/gi;
        const matches = text.match(regex) || [];
        return [...new Set(matches)].slice(0, 50); // dedupe + cap at 50
    };

    // --- Smart Paste ---
    // If pasted text has 2+ tweet links, clear inputs and fill them all in
    tweetInputsContainer.addEventListener('paste', (e) => {
        const pasted = (e.clipboardData || window.clipboardData).getData('text');
        const links = extractTweetLinks(pasted);

        if (links.length < 2) return; // single link: let the browser handle it normally

        e.preventDefault();

        tweetInputsContainer.innerHTML = '';
        links.forEach((link, i) => {
            tweetInputsContainer.appendChild(createInputGroup(i + 1, link));
        });
        setCount(links.length);
    });

    // --- Counter buttons ---
    incrementBtn.addEventListener('click', () => {
        if (count < 50) {
            setCount(count + 1);
            updateInputs();
        }
    });

    decrementBtn.addEventListener('click', () => {
        if (count > 1) {
            setCount(count - 1);
            updateInputs();
        }
    });

    // --- Generate ---
    generateBtn.addEventListener('click', async () => {
        const inputs = tweetInputsContainer.querySelectorAll('.tweet-input');
        const urls = Array.from(inputs)
            .map(input => input.value.trim())
            .filter(u => u && u !== '...');

        if (urls.length === 0) {
            alert('Please enter at least one tweet link.');
            return;
        }

        const originalText = generateBtn.textContent;
        generateBtn.textContent = 'Scraping & Generating...';
        generateBtn.disabled = true;

        try {
            const tweetsData = [];
            const results = [];

            for (const url of urls) {
                try {
                    let apiUrl = url;
                    if (url.includes('x.com')) {
                        apiUrl = url.replace('x.com', 'api.vxtwitter.com');
                    } else if (url.includes('twitter.com')) {
                        apiUrl = url.replace('twitter.com', 'api.vxtwitter.com');
                    } else {
                        apiUrl = `https://api.vxtwitter.com/status/${url}`;
                    }

                    const scrapeRes = await fetch(apiUrl);
                    if (scrapeRes.ok) {
                        const data = await scrapeRes.json();
                        const text = data.text;
                        const username = data.user_screen_name;

                        if (text && username) {
                            tweetsData.push({ id: url, text: `@${username} | ${text}` });
                        } else {
                            results.push({ url, reply: 'Error: Could not extract tweet content', status: 'error' });
                        }
                    } else {
                        results.push({ url, reply: `Error: Scrape failed (${scrapeRes.status})`, status: 'error' });
                    }
                } catch (err) {
                    console.error(`Scrape error for ${url}:`, err);
                    results.push({ url, reply: `Error: Scrape failed (${err.message})`, status: 'error' });
                }
            }

            if (tweetsData.length === 0) {
                resultsBody.innerHTML = '';
                results.forEach(res => {
                    const row = document.createElement('tr');
                    row.innerHTML = `<td>${res.url}</td><td>${res.reply}</td><td><span style="color:#e55">Error</span></td>`;
                    resultsBody.appendChild(row);
                });
                return;
            }

            const response = await fetch('/api/generate-replies', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tweets: tweetsData, tone: 'professional' }),
            });

            if (!response.ok) throw new Error('Backend generation failed');

            const data = await response.json();
            const finalResults = [...results, ...data.results];

            resultsBody.innerHTML = '';
            finalResults.forEach(res => {
                const row = document.createElement('tr');
                const isError = res.status === 'error';
                row.innerHTML = `
                    <td>${res.url || res.id}</td>
                    <td>${res.reply}</td>
                    <td>
                        ${isError
                            ? '<span style="color:#e55">Error</span>'
                            : `<a class="post-btn" href="https://twitter.com/intent/tweet?text=${encodeURIComponent(res.reply)}" target="_blank" rel="noopener">Post</a>`
                        }
                    </td>
                `;
                resultsBody.appendChild(row);
            });

        } catch (error) {
            console.error('Error:', error);
            alert('Error generating replies. Check console for details.');
        } finally {
            generateBtn.textContent = originalText;
            generateBtn.disabled = false;
        }
    });
});
