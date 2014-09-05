// Begin jQuery functions
$(function() {
    $('#btnSearch').click(function() {
        Search();
    });
    $(document).ready(function(){
	Search();
    });
    // Replace the following string with the AppId you received from the
    // Bing Developer Center.
    var AppId = "AppId=D41D8CD98F00B204E9800998ECF8427E7F102AF6";
    var Query = "Query="
    var Sources = "Sources=Web+Image+Video";
    var Version = "Version=2.2";
    var Market = "Market=en-US"; // I'm a Kiwi.  You may want to change your localisation.
    var Options = "Options=EnableHighlighting";
    var WebCount = 3;
    var WebOffset = 0;


    function Search() {
        var searchTerms = $('#txtQuery').val().replace(" ", "+");
		searchTerms = encodeURI(searchTerms);   
        var arr = [AppId, Query + searchTerms, Sources, Version, Market, Options, "Web.Count=" + WebCount, "Web.Offset=" + WebOffset, "Image.Count=" + WebCount , "Video.Count=" + WebCount , "JsonType=callback", "JsonCallback=?"];
        var requestStr = "http://api.bing.net/json.aspx?" + arr.join("&");

        $.ajax({
            type: "GET",
            url: requestStr,
            dataType: "jsonp",
            success: function(msg) {
                SearchCompleted(msg);
            },
            error: function(msg) {
                alert("Something hasn't worked\n" + msg.d);
            }
        });
    }

    function SearchCompleted(response) {

        var errors = response.SearchResponse.Errors;
        if (errors != null) {
            // There are errors in the response. Display error details.
            DisplayErrors(errors);
        }
        else {
            // There were no errors in the response. Display the Web results.
            DisplayResults(response);
        }
    }

    function DisplayResults(response) {
        $("#result-list").html("");                                 // Clear our existing results
        $("#result-navigation li").filter(".nav-page").remove();    // Remove our navigation
        $("#result-aggregates").children().remove();                // Remove our hit information

        var results = response.SearchResponse.Web.Results;          // Define our web results in a more succinct way

        // Let the user know what they searched for and what the search yielded
//        $('#result-aggregates').prepend("<p>检索词： " + response.SearchResponse.Query.SearchTerms + "</p>");
  //      $('#result-aggregates').prepend("<p id=\"result-count\">当前显示 " + StartOffset(results)
  //          + " 至 " + EndOffset(results)
   //         + "&nbsp;&nbsp;总共:" + parseInt(response.SearchResponse.Web.Total) + "</p>");

        // Create the list of results
        var link = [];
	var l = 0;                                  // We'll create each link in this array
        var regexBegin = new RegExp("\uE000", "g");     // Look for the starting bold character in the search response
        var regexEnd = new RegExp("\uE001", "g");       // Look for the ending bold character in the search response
        for (var i = 0; i < results.length; ++i) {
            // Step through our list of results and build our list items
            link[i] = "<div class=\"col-md-4\"><a href=\"" + results[i].Url + "\" title=\"" + results[i].Title + "\">"
                + results[i].Title + "</a>"
                + "<p>" + results[i].Description + "</p>"
                + "<p class=\"result-url\">" + results[i].Url + "</p></div>";

            // Replace our unprintable bold characters with HTML
            link[i] = link[i].replace(regexBegin, "<strong>").replace(regexEnd, "</strong>");
        }

	$("#result-list-web").html(link.join(''));

	link = []; l = 0;
	//l = l + results.length;
	results = response.SearchResponse.Image.Results;
	for (var i = 0;i < results.length; ++i) {
		link[l+i] = "<div class = \"col-md-4\"><a href=\"" + results[i].Url + "\" title=\"" + results[i].Title + "\">"
		+ results[i].Title + "</a>"
	        +"<p></p>"
		/*+"<p>" + results[i].Description + "</p>"*/
		+ "<img src=\"" + results[i].Thumbnail.Url + "\" width = 200 height = 200/>";
		
		link[l+i] = link[l+i].replace(regexBegin , "<strong>").replace(regexEnd,"</strong>") + "</div>";
	}
 	
	$("#result-list-image").html(link.join(''));

	link = []; l = 0;
	//l = l + results.length;
        results = response.SearchResponse.Video.Results;
        for (var i = 0;i < results.length; ++i) {
                link[l+i] = "<div class = \"col-md-4\"><a href=\"" + results[i].PlayUrl + "\" title=\"" + results[i].Title + "\">"
                + results[i].Title + "</a>"
                +"<p></p>"+
		"<a href=\"" + results[i].PlayUrl + "\" title=\"" + "\">"
                + "<img src=\"" + results[i].StaticThumbnail.Url + "\" width = 200 height = 200/>" +
                "</a>"+"</div>"
                /*+"<p>" + results[i].Description + "</p>"*/
                ;

                link[l+i] = link[l+i].replace(regexBegin , "<strong>").replace(regexEnd,"</strong>");
        }


	$("#result-list-video").html(link.join(''));
        // Set up our result page navigation 
        //CreateNavigation(response.SearchResponse.Web.Total, results.length);
    }

    function StartOffset(results) {
        if (WebOffset == 0) {
            return 1;
        }
        else {
            return (WebOffset * results.length) + 1;
        }
    }

    function EndOffset(results) {
        if (WebOffset == 0) {
            return results.length;
        }
        else {
            return (WebOffset + 1) * results.length;
        }
    }

    function CreateNavigation(totalHits, pageSize) {
        var totalPages = (totalHits / pageSize > 10) ? 10 : parseInt(totalHits / pageSize);
        var nav = [];
        for (var i = 0; i < totalPages; i++) {
            nav[i] = "<li class=\"nav-page\">" + (i + 1) + "</li>";
        }
        $("#result-navigation li:first").after(nav.join(''));

        // Create a listener for the page navigation click event
        $("#result-navigation li.nav-page").click(function() {
            WebOffset = parseInt($(this).html()) - 1;
            Search();
        });

        // Show the navigation!
        $("#result-navigation").show();
    }

    $("#prev").click(function() {
        if (WebOffset > 1) WebOffset--;
        Search();
    });

    $("#next").click(function() {
        WebOffset++;
        Search();
    });

    function DisplayErrors(errors) {
        var errorHtml = [];

        for (var i = 0; i < errors.length; ++i) {
            errorHtml[i] = "<li>" + errors[i] + "</li>";
        }
        $('#error-list').append(errorHtml.join(''));
    }
});

