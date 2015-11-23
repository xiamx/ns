google.load('search', '1');
var newsSearch;
var searchtopic;

google.setOnLoadCallback(function(){
    google.search.Search.getBranding('branding');
    
});
var cxhr;

var getSummary = function(){
    if (cxhr) {
        cxhr.abort();
    }
    var searchComplete = function(){
        var links = _.map(newsSearch.results, function(r){
            return unescape(r.url);
        })
        
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
        }).done(function(data){
            var summaryEl = document.getElementById("summary");
            summaryEl.innerHTML = "";
            var p = document.createElement("p");
            p.innerHTML = data.summary
            summaryEl.appendChild(p);
            var sourcesEl = document.createElement("div");
            sourcesEl.className = "sources";
            var ul = document.createElement("ul");
            var lis = _.map(links, function(l){
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
            
        }).fail(function(data){
            document.getElementById("summary").innerHTML = "Oops, something went wrong and I can't build a summary";
        });
        
    }
    newsSearch = new google.search.NewsSearch();
    newsSearch.setSearchCompleteCallback(this, searchComplete, null);
    searchtopic = document.querySelector("#topic").value;
    newsSearch.execute(searchtopic);
    document.getElementById("summary").innerHTML="Building a summary...";
    
}

document.querySelector("#topic").addEventListener(
    "keypress", function(event) {
        if (event.keyCode === 13) {
            getSummary();
        }
    })

// document.querySelector("#topic").addEventListener(
//     "keypress", _.debounce(getSummary, 500))