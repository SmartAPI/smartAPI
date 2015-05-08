var app = angular.module('myApp', ['autocomplete']);

// the service that retrieves some movie title from an url
app.factory('MovieRetriever', function($http, $q, $timeout){
  var MovieRetriever = new Object();

  MovieRetriever.getmovies = function(i) {
    var moviedata = $q.defer();
    var movies;

    var moreMovies = [];

    if(i && i.indexOf('T')!=-1)
      movies=moreMovies;
    else
      movies=moreMovies;

    $timeout(function(){
      moviedata.resolve(movies);
    },1000);

    return moviedata.promise
  }

  return MovieRetriever;
});




app.controller('MyCtrl', function($scope, $http, $q, MovieRetriever){

    $scope.updateOntos = function(typedthings){

        //HTTP REQUEST
        $scope.url1 = "http://data.bioontology.org/search?apikey=8d6c5698-db6b-4b7d-a8e3-b3b8b949ca3a&display_links=true&display_context=false&q=" + typedthings;
        var req1 = $http.get($scope.url1);
        req1.success(function(data, status) {
            $scope.concepts = data.collection;
            $scope.arr1 = [];
            $scope.ontos = [];
            for(i=0,count=$scope.concepts.length; i<count;i++) {
                //new array
                $scope.arr1[i] = {
                                    prefLabel: $scope.concepts[i].prefLabel,
                                    ontology: $scope.concepts[i].links.ontology
                                 };
                ontoFunction(i);
            }
        });

        var ontoFunction = function(index){

                //HTTP Request
                $scope.url2 = $scope.concepts[index].links.ontology + "?apikey=8d6c5698-db6b-4b7d-a8e3-b3b8b949ca3a&display_links=false&display_context=false";
                var req2 = $http.get($scope.url2);

                req2.success(function(data, status) {
                    $scope.arr1[index].ontoName = data.name;
                    $scope.arr1[index].ontoAcro = data.acronym;
                    $scope.movies[index] = index + " " + $scope.arr1[index].prefLabel + " [" + $scope.arr1[index].ontoAcro + "]";
                });

                req2.error(function(data, status) {
                    //console.log(data);
                });

        };

    };


    
    $scope.movies = MovieRetriever.getmovies("...");
    $scope.movies.then(function(data){
        $scope.movies = data;
    });

    $scope.getmovies = function(){
        return $scope.movies;
    }

    $scope.updateMovies = function(typedthings){
        //console.log("Do something like reload data with this: " + typedthings );
        $scope.updateOntos(typedthings);
        $.newmovies = MovieRetriever.getmovies(typedthings);
        $scope.newmovies.then(function(data){
            $scope.movies = data;
        });
    }

    $scope.doSomethingElse = function(suggestion){
        console.log("Suggestion selected: " + suggestion );
    }
    
});
