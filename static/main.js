google.load('search', '1');
var newsSearch;
var searchtopic;

google.setOnLoadCallback(function() {
    google.search.Search.getBranding('branding');

});
var cxhr;

var getSummary = function() {
    if (cxhr) {
        cxhr.abort();
    }
    var FEED_URL = "https://news.google.com/news/section?q=election&output=rss"
    $.get(FEED_URL, function (data) {
        $(data).find("entry").each(function () { // or "item" or whatever suits your feed
            var el = $(this);
    
            console.log("------------------------");
            console.log("title      : " + el.find("title").text());
            console.log("author     : " + el.find("author").text());
            console.log("description: " + el.find("description").text());
        });
    });
    return;
    var searchComplete = function() {
        var majorityLanguage = function() {
            var languageCount = _.countBy(newsSearch.results, function(r) {
                return r.language;
            });
            return _.max(_.pairs(languageCount), function(lancountpair) {
                return lancountpair[1];
            })[0];
        }();
        var links = _.map(_.filter(newsSearch.results, function(r) {
            return r.language === majorityLanguage;
        }), function(r) {
            return unescape(r.url);
        });

        var outputfail = function() {
            document.getElementById("summary").innerHTML = "Oops, something went wrong and I can't build a summary";
        }

        var fetchResult = function(tid, ntry) {
            var rxhr = $.ajax({
                type: 'GET',
                url: 'getsummary' + '/' + tid,
                contentType: "application/json",
                dataType: 'json'
            }).done(function(data) {
                if (data.status === "done") {
                    var summaryEl = document.getElementById("summary");
                    summaryEl.innerHTML = "";
                    var p = document.createElement("p");
                    p.innerHTML = data.summary
                    summaryEl.appendChild(p);
                    
                    if (data.images && data.images[0]){
                        var mainimg = document.createElement("img");
                        mainimg.setAttribute("src", data.images[0])
                        mainimg.className = "mainimage"
                        summaryEl.appendChild(mainimg)
                    }
                    
                    var sourcesEl = document.createElement("div");
                    sourcesEl.className = "sources";
                    var ul = document.createElement("ul");
                    var lis = _.map(links, function(l) {
                        var li = document.createElement("li");
                        li.innerHTML = l;
                        return li
                    });
                    _.each(lis, ul.appendChild, ul);
                    var sourcep = document.createElement("p");
                    sourcep.innerHTML = "<br/>Sources:"
                    sourcesEl.appendChild(sourcep);
                    sourcesEl.appendChild(ul);
                    summaryEl.appendChild(sourcesEl);
                }
                else {
                    if (ntry < 25) {
                        setTimeout(fetchResult, 1000, tid, ntry + 1);
                    }
                    else {
                        outputfail();
                    }

                }

            }).fail(outputfail);
        }
        cxhr = $.ajax({
            type: 'POST',
            url: 'summarize',
            contentType: "application/json",
            data: JSON.stringify({
                topic: searchtopic,
                links: links,
                words: 100
            }),
            dataType: 'json'
        }).done(function(data) {
            fetchResult(data.task, 0);

        }).fail(outputfail);

    }
    newsSearch = new google.search.NewsSearch();
    newsSearch.setSearchCompleteCallback(this, searchComplete, null);
    searchtopic = document.querySelector("#topic").value;
    newsSearch.execute(searchtopic);
    document.getElementById("summary").innerHTML = "Building a summary...";

}

document.querySelector("#topic").addEventListener(
    "keypress",
    function(event) {
        if (event.keyCode === 13) {
            getSummary();
        }
    })

// document.querySelector("#topic").addEventListener(
//     "keypress", _.debounce(getSummary, 500))