
var searchFilter = '';

$(document).ready(function() {
  searchInit();

  // Register the search button to act upon a enter keystroke  
  $('#search-nav-btn').keypress(function(e) {
      if(e.which == 13) {
          window.location.href = "http://umbel.org/search/?query="+$("#search-nav-btn").val() + (searchFilter != '' ? '&f=' + searchFilter : '');
      }
  });
  
  $('#search-input').keypress(function(e) {
      if(e.which == 13) {
          window.location.href = "http://umbel.org/search/?query="+$("#search-input").val() + (searchFilter != '' ? '&f=' + searchFilter : '');
      }
  });
  
});

function searchInit()
{
  var urlVars = getUrlVars();
  
  var query = "";
  
  if(urlVars["f"] != undefined)
  {
    searchFilter = urlVars["f"];

    switch(searchFilter)
    {
      case 'pref-label':
        $('#type-search-tip').html('Preferred label')
      break;
      case 'alt-labels':
        $('#type-search-tip').html('Alternative labels')
      break;
      case 'Description':
        $('#type-search-tip').html('Description')
      break;
      case 'uri':
        $('#type-search-tip').html('URI')
      break;
    }    
  }  
  
  if(urlVars["query"] != undefined)
  {
    query = urlVars["query"];
    
    $("#search-nav-btn").val(unescape(query));    
    
    search();
  }  
  
  $("#search-btn").click(function() {
    window.location.href = "http://umbel.org/search/?query="+$("#search-input").val() + (searchFilter != '' ? '&f=' + searchFilter : '');
  });
  
  // Initialize search filters buttons
  $("#search-filter-preflabel").click(function(){
    searchFilter = 'pref-label';
    $('#type-search-tip').html('Preferred label')
  });
  
  $("#search-filter-altlabels").click(function(){
    searchFilter = 'alt-labels';
    $('#type-search-tip').html('Alternative labels')
  });
  
  $("#search-filter-description").click(function(){
    searchFilter = 'description';
    $('#type-search-tip').html('Description')
  });
  
  $("#search-filter-uri").click(function(){
    searchFilter = 'uri';
    $('#type-search-tip').html('URI')
  });
    
  $("#search-filter-all").click(function(){
    searchFilter = '';
    $('#type-search-tip').html('All')
  });  
}
  
  
function search()
{
  if($("#search-nav-btn").val() == "")
  {
    return;
  }                
  
  $('#results-list').empty();
  
  var query = $("#search-nav-btn").val();
  
  
  if(searchFilter == '' && query.search(/[~\+(OR)(AND)(NOT)(TO)^\-:\[\]]/) == -1)
  {
    query = 'pref-label:"'+query+'"^10 OR alt-label:"'+query+'"^6 OR description:"'+query+'"^3 OR uri:"'+query+'"^1';
  }
    
  // Get the results
  $.ajax({                          
    type: "GET",
    url: "http://umbel.org/ws/search/" + (searchFilter != '' ? searchFilter + ':' : '') + query + "/page/" + (getPage() - 1),
    dataType: "json",
    success: function(results)
    {
      var nbResults = results['results'].length;
   
      // Display the number of results
      if(nbResults == 0)
      {
        $("#panel-results-header").empty().append("No results found for this query");
      }
      else
      {
        if(results['nb-results'] <= 10)
        {
          $("#panel-results-header").empty().append(nbResults + " results");
        }
        else
        {
          $("#panel-results-header").empty().append((1 + ((getPage() - 1) * 10))+" - "+((getPage() * 10) > results['nb-results'] ? results['nb-results'] : (getPage() * 10))+" of " + results['nb-results'] + " results");
        }
      }
      
      // Display paginators
      var options = {
          currentPage: getPage(),
          totalPages: Math.ceil(results['nb-results'] / 10),
          bootstrapMajorVersion: 3,
          numberOfPages: 7,
          pageUrl: function(type, page, current){

              return "http://umbel.org/search/?query="+$("#search-nav-btn").val()+"&page="+page+(searchFilter != '' ? '&f=' + searchFilter : '');

          }
      }

      $('#panel-paginator-header').bootstrapPaginator(options);      
      
      // Display the actual results
      for(var i = 0; i < results['results'].length; i++)
      {
        var record = results['results'][i];
        
        var label = '';
        var path = '';
        
        var module = 'Core';
        var moduleBadge = 'info';
        var moduleTitleInfo = 'This concept belongs to UMBEL Core';
        
        switch(record['is-defined-by'])
        {
          case 'http://umbel.org/umbel/geo#':
            module = 'Geo';
            moduleBadge = 'success';
            moduleTitleInfo = 'This concept belongs the UMBEL Geo module';
          break;
          case 'http://umbel.org/umbel/attributes#':
            module = 'Attributes';
            moduleBadge = 'success';
            moduleTitleInfo = 'This concept belongs the UMBEL Attributes module';
          break;
          case 'http://umbel.org/umbel/entities#':
            module = 'Entities';
            moduleBadge = 'success';
            moduleTitleInfo = 'This concept belongs the UMBEL Entities module';
          break;
        }        
        
        if(record['uri'].indexOf('umbel/rc') == -1)
        {
          label = '<span class="label label-'+ moduleBadge +' pull-right" style="margin-left: 5px" title="'+moduleTitleInfo+'">'+module+'</span><span class="label label-success pull-right" title="'+record['uri']+'">Super Type</span>';
          path = 'super-type';
        }
        else
        {
          label = '<span class="label label-'+ moduleBadge +' pull-right" style="margin-left: 5px" title="'+moduleTitleInfo+'">'+module+'</span><span class="label label-info pull-right" title="'+record['uri']+'">Reference Concept</span>';
          path = 'reference-concept';
        }
        
        $('#results-list').append('<a href="http://umbel.org/'+path+'/?uri='+urlencode(getConceptEnding(record['uri']))+'" class="list-group-item">\
                                     <h4 class="list-group-item-heading">'+record['pref-label']+' &nbsp;&nbsp; '+label+'</h4>\
                                     <div>&nbsp;</div>\
                                     <p class="list-group-item-text">'+record['description']+'</p>\
                                   </a>');
      }         
    },
    error: function(jqXHR, textStatus, error)
    {
      /*
      $('#messagesContainer').fadeOut("fast", function()
      {
        $('#messagesContainer').empty();
      });

      var error = JSON.parse(jqXHR.responseText);

      var errorMsg = '[' + error.id + '] ' + error.name + ': ' + error.description;

      $('#messagesContainer').append('<div class="errorBox">' + errorMsg + '</div>').hide().fadeIn("fast");
      */
    }
  });  
}

function getUrlVars()
{
    var vars = [], hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for(var i = 0; i < hashes.length; i++)
    {
        hash = hashes[i].split('=');
        vars.push(hash[0]);
        vars[hash[0]] = hash[1];
    }
    return vars;
}

function getPage()
{
  urlVars = getUrlVars();
  if(urlVars["page"] != undefined)
  {
    return(urlVars["page"]);
  }
  else
  {
    return(1)
  }  
}

function getConceptEnding(concept)
{
  if(concept.indexOf('#') != -1)
  {
    return(concept.substring(concept.lastIndexOf('#') + 1));
  }
  else
  {
    return(concept.substring(concept.lastIndexOf('/') + 1));
  }
}

function urlencode(str)
{
// http://kevin.vanzonneveld.net
// +   original by: Philip Peterson
// +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
// +      input by: AJ
// +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
// +   improved by: Brett Zamir (http://brett-zamir.me)
// +   bugfixed by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
// +      input by: travc
// +      input by: Brett Zamir (http://brett-zamir.me)
// +   bugfixed by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
// +   improved by: Lars Fischer
// +      input by: Ratheous
// +      reimplemented by: Brett Zamir (http://brett-zamir.me)
// +   bugfixed by: Joris
// +      reimplemented by: Brett Zamir (http://brett-zamir.me)
// %          note 1: This reflects PHP 5.3/6.0+ behavior
// %        note 2: Please be aware that this function expects to encode into UTF-8 encoded strings, as found on
// %        note 2: pages served as UTF-8
// *     example 1: urlencode('Kevin van Zonneveld!');
// *     returns 1: 'Kevin+van+Zonneveld%21'
// *     example 2: urlencode('http://kevin.vanzonneveld.net/');
// *     returns 2: 'http%3A%2F%2Fkevin.vanzonneveld.net%2F'
// *     example 3: urlencode('http://www.google.nl/search?q=php.js&ie=utf-8&oe=utf-8&aq=t&rls=com.ubuntu:en-US:unofficial&client=firefox-a');
// *     returns 3: 'http%3A%2F%2Fwww.google.nl%2Fsearch%3Fq%3Dphp.js%26ie%3Dutf-8%26oe%3Dutf-8%26aq%3Dt%26rls%3Dcom.ubuntu%3Aen-US%3Aunofficial%26client%3Dfirefox-a'
  str = (str + '').toString();

// Tilde should be allowed unescaped in future versions of PHP (as reflected below), but if you want to reflect current
// PHP behavior, you would need to add ".replace(/~/g, '%7E');" to the following.
  return encodeURIComponent(str).replace(/!/g, '%21').replace(/'/g, '%27').replace(/\(/g, '%28').replace(/\)/g,
    '%29').replace(/\*/g, '%2A').replace(/%20/g, '+');
}
           
