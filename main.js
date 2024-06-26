function setSummary(text) {
    document.getElementById("summary").innerHTML = text;
    document.getElementById("progress").remove();
}

chrome.tabs.query({ active: true, currentWindow: true }).then(function (tabs) {
    return chrome.scripting.executeScript({ target: { tabId: tabs[0].id }, func: function() {
        let result = "";

        for (element of document.body.querySelectorAll("h1, h2, h3, h4, h5, h6, p")) {
            result += element.innerHTML + " ";
        }

        return result;
    } });
}).then(function (result) {
    let port = chrome.runtime.connectNative("com.isaac.summarizer");

    port.onMessage.addListener(function (message) {
        progress = parseFloat(message);

        if (isNaN(progress)) {
            setSummary(message);

            port.disconnect();
        }

        else {
            percent = Math.floor(progress * 100) + "%";

            document.getElementById("progress-fill").style.width = percent;
            document.getElementById("progress-number").innerHTML = percent;
        }
    });

    port.onDisconnect.addListener(function () {
        setSummary("Error creating summary: " + chrome.runtime.lastError.message);
    });

    let formatted = result[0].result.replaceAll(new RegExp("<.+?>|</.+?>|&.+?;|\\s+", "g"), " ").trim();

    port.postMessage(Math.ceil(formatted.length / 50000));

    for (let i = 0; i < formatted.length; i += 50000) {
        port.postMessage(formatted.substring(i, Math.min(i + 50000, formatted.length)));
    }
}).catch(function (error) {
    setSummary("Error parsing page: " + error);
});
