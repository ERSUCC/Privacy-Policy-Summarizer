function removeTags(string) {
    return string.replaceAll(new RegExp("<.+?>|</.+?>", "g"), "");
}

chrome.tabs.query({ active: true, currentWindow: true }).then(function (tabs) {
    return chrome.scripting.executeScript({ target: { tabId: tabs[0].id }, func: function() {
        return document.body.innerHTML;
    } })
}).then(function (result) {
    let headings = document.createElement("ul");

    for (match of result[0].result.matchAll(new RegExp("<h.>(.+?)</h.>", "g"))) {
        let element = document.createElement("li");

        element.innerHTML = removeTags(match[1]);

        headings.appendChild(element);
    }

    document.getElementById("headings").appendChild(headings);
}).catch(function (error) {
    console.log(error);

    document.getElementById("headings").appendChild(document.createTextNode("Error parsing page."));
});
