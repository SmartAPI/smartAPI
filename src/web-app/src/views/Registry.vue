<template>
  <main class="white">
  <div id="app" style="height: 100%;" class="white container-fluid" v-cloak>
    <MetaHead title="SmartAPI | API Registry"></MetaHead>
    <!-- Loading Screen -->
    <div v-show="loading" class="center-align loader">
      <div class="center-align">
        <div class="lds-ellipsis"><div></div><div></div><div></div><div></div></div>
      </div>
    </div>
      <div class="row">
        <div class="col l2 s12 hide-on-med-and-down hide-on-small-only sidebar">
            <h5 class="blue-text center"> Filters</h5>
            <ul class="collapsible">
              <li>
                <div class="collapsible-header blue-grey white-text">
                  <span>Tags (<b>{{tags.length}}</b>)</span>
                </div>
                <div class="collapsible-body noPadding">
                  <div class="collection">
                      <!-- Search Box -->
                      <div class="input-field collection-item">
                        <input v-model="tagsearch" placeholder="Search" id="fs" type="text">
                        <button @click.prevent="listAll = !listAll" class="smallButton grey" >
                          <small v-if="!listAll">Show All ({{tags.length - listCap}} more)</small>
                          <small v-if="listAll">Show Less (Only 20)</small>
                        </button>
                      </div>
                      <!-- If searching - Results -->
                      <template v-for="tag in tagSearchResults" :key="tag">
                        <a  v-if="tagsearch.length" class="collection-item"
                            style="padding:2px;"
                            :class="{ disable: tag.name.toLowerCase() === specialTagOriginalName.toLowerCase(), active: tag.active, blue: tag.active  && tag.name.toLowerCase() !== specialTagOriginalName.toLowerCase(), green: tag.active  && tag.name.toLowerCase() === specialTagOriginalName.toLowerCase() , 'white-text': tag.active}"
                            href="#!"
                            @click.prevent="toggleTag(tag,'tag');search(); googleAnalytics('Registry_Tag', tag.name)">
                          <small>{{tag.name}}  <span class="bold">({{tag.count}})</span></small>
                        </a>
                      </template>
                      <!-- no search - ALL -->
                      <template v-if="!tagsearch.length">
                        <template v-for="(tag,index) in tags" :key="tag+index">
                            <a  v-if="index < listCap"
                                class="collection-item"
                                style="padding:2px;"
                                :class="{ disable: tag.name.toLowerCase() === specialTagOriginalName.toLowerCase(), active: tag.active, blue: tag.active  && tag.name.toLowerCase() !== specialTagOriginalName.toLowerCase(), green: tag.active  && tag.name.toLowerCase() === specialTagOriginalName.toLowerCase() , 'white-text': tag.active}"
                                href="#!"
                                @click.prevent="toggleTag(tag,'tag');search(); googleAnalytics('Registry_Tag', tag.name)">
                            <small>{{tag.name}}  <span class="bold">({{tag.count}})</span></small>
                            </a>
                        </template>
                      </template>
                      

                  </div>
                </div>
              </li>

              <li>
                <div class="collapsible-header blue-grey white-text">
                  <span>Owners (<b>{{authors.length}}</b>)</span>
                </div>
                <div class="collapsible-body noPadding">
                  <div class="collection">
                      <!-- Search Box -->
                      <div class="input-field collection-item">
                        <input v-model="ownersearch" placeholder="Search" id="os" type="text">
                        <button @click.prevent="listAll = !listAll" class="smallButton grey" >
                          <small v-if="!listAll">Show All ({{authors.length - listCap}} more)</small>
                          <small v-if="listAll">Show Less (Only 20)</small>
                        </button>
                      </div>
                      <!-- If searching - Results -->
                      <template v-if="ownersearch.length">
                        <template v-for="tag in ownerSearchResults" :key="tag">
                            <a  class="collection-item"
                                style="padding:2px;"
                                :class="{ disable: tag.name.toLowerCase() === specialTagOriginalName.toLowerCase(), active: tag.active, blue: tag.active  && tag.name.toLowerCase() !== specialTagOriginalName.toLowerCase(), green: tag.active  && tag.name.toLowerCase() === specialTagOriginalName.toLowerCase() , 'white-text': tag.active}"
                                href="#!"
                                @click.prevent="toggleTag(tag,'author');search(); googleAnalytics('Registry_Tag', tag.name)">
                            <small>{{tag.name}}  <span class="bold">({{tag.count}})</span></small>
                            </a>
                        </template>
                      </template>
                      <!-- no search - ALL -->
                      <template v-if="!ownersearch.length">
                        <template v-for="(tag,index) in authors" :key="tag+index">
                            <a  v-if="index < listCap"
                                class="collection-item"
                                style="padding:2px;"
                                :class="{ disable: tag.name.toLowerCase() === specialTagOriginalName.toLowerCase(), active: tag.active, blue: tag.active  && tag.name.toLowerCase() !== specialTagOriginalName.toLowerCase(), green: tag.active  && tag.name.toLowerCase() === specialTagOriginalName.toLowerCase() , 'white-text': tag.active}"
                                href="#!"
                                @click.prevent="toggleTag(tag,'author');search(); googleAnalytics('Registry_Tag', tag.name)">
                            <small>{{tag.name}}  <span class="bold">({{tag.count}})</span></small>
                            </a>
                        </template>
                      </template>
                      

                  </div>
                </div>
              </li>
            </ul>

            <ul class="collection" style="margin-top:100px;" v-show="popularTags && popularTags.length > 5">
              <div class="collection-header blue-grey white-text p-1 center-align">
                <span>Filters Most Active <br />(Last 30 days)</span>
              </div>
              <template v-for="(pop,index) in popularTags" :key="pop+index">
                  <a v-if="index < 10" :href="pop.type == 'tags'?'/registry?tags='+pop.name:'/registry?owners='+pop.name" :class="{ active: pop.active, blue: pop.active, bold:index==0 }" :title="pop.count" @click="googleAnalytics('Registry_Tag', pop.name)" class="collection-item" style="padding:4px;" >
                  {{index+1}} <small><span v-text="pop.type == 'tags' ? '#' : '@'"></span> <span v-text="pop.name"></span></small>
                </a>
              </template>
            </ul>

            <!-- <ul class="collection" style="margin-top:50px;">
              <div class="collection-header purple white-text p-1 center-align">
                <span>Portal Specific</span>
              </div>
              <router-link class="collection-item left-align" to='/registry/translator'>Translator</router-link>
              <router-link class="collection-item left-align" to='/registry/nihdatacommons'>NIH Data Commons</router-link>
            </ul> -->

        </div>
        <div class="col s12 hide-on-med-and-up show-on-small-only">
            <ul class="collapsible">
              <li>
                <div class="collapsible-header blue-grey white-text">
                  <small>Filter by Tags</small>
                </div>
                <div class="collapsible-body noPadding">
                  <div class="collection">
                    <div class="colllection-item padding20">
                      <template v-for="tag in tags" :key="tag">
                        <a class="chip" :class="{ disable: tag.name.toLowerCase() === specialTagOriginalName.toLowerCase(), active: tag.active, blue: tag.active  && tag.name.toLowerCase() !== specialTagOriginalName.toLowerCase(), green: tag.active  && tag.name.toLowerCase() === specialTagOriginalName.toLowerCase() , 'white-text': tag.active}" href="#!"  @click.prevent="tag.active = !tag.active;search(); googleAnalytics('Registry_Tag', tag.name)">{{tag.name}}  <span class="bold">({{tag.count}})</span></a>
                      </template>
                    </div>
                  </div>
                </div>
              </li>
              <li>
                <div class="collapsible-header blue-grey white-text center-align">
                  <small>Filter by Owners</small>
                </div>
                <div class="collapsible-body noPadding">
                  <div class="collection">
                    <div class="colllection-item padding20">
                      <template v-for="author in authors" :key="author">
                        <a :class="{ active: author.active, blue: author.active }" href="#!" class="chip" @click.prevent="author.active = !author.active;search(); googleAnalytics('Registry_Author', author.name)">{{author.name}}  <span class="bold">({{author.count}})</span> <span class="red-text" v-if="userInfo && author.name === userInfo.name">(Me)</span></a>
                      </template>
                    </div>
                  </div>
                </div>
              </li>
            </ul>
        </div>
        <div class="col s12 l10">
          <div class="row">
            <form class="col s12 center-align" @submit.prevent="search()" id="api_search_form">
              <template v-if='specialTagsUI'>
                <div  class="col s12 l3 input-field center-align">
                  <a class='tooltipped p-1' data-position="bottom" :data-tooltip="'Learn More about '+specialTagName" :href="specialTagURL" target="_blank" style="cursor: pointer !important;">
                      <template v-if="specialTagsUI && portal_name">
                          <Image style="max-width:200px" img_height="auto" img_width="100%" :img_name="specialTagImage" :alt="specialTagName"></Image>
                      </template>
                  </a>
                  <div v-if="specialTagName == 'NCATS Biomedical Data Translator'">
                    <router-link class="purple-text d-block" :to="'/portal/'+portal_name">
                      Go to portal <i class="fa fa-chevron-right" aria-hidden="true"></i>
                    </router-link>
                  </div>
                </div>
                <div class="input-field col s12 l6">
                    <input aria-required="false" required='false' id="search_query" type="text" v-model="query" name="query" placeholder="Enter any query term here" class="browser-default margin20 grey lighten-5 blue-grey-text lighter" style="width: 80%; outline: none; padding: 10px; border-radius: 20px; border:var(--blue-medium) 2px solid;">
                </div>
              </template>
              <template v-else>
                <div class="input-field col s12 l6 offset-l3">
                    <input aria-required="false" required='false' id="search_query" type="text" v-model="query" name="query" placeholder="Enter any query term here" class="browser-default margin20 grey lighten-5 blue-grey-text lighter" style="width: 80%; outline: none; padding: 10px; border-radius: 20px; border:var(--blue-medium) 2px solid;">
                </div>
              </template>

                <div class="col s12 selected-tags">
                    <template v-for="tag in tags" :key="tag">
                      <div class="chip" v-if="tag.active" :class="{ purple: tag.name.toLowerCase() === specialTagOriginalName.toLowerCase(), 'white-text': tag.name.toLowerCase() === specialTagOriginalName.toLowerCase() }">
                          {{tag.name}}
                          <i v-if="tag.name.toLowerCase() !== specialTagOriginalName.toLowerCase()" class="close material-icons" @click="toggleTag(tag,'tag');search()">close</i>
                      </div>
                    </template>
                    <template v-for="author in authors" :key="author">
                      <div class="chip" v-if="author.active">
                          {{author.name}}
                          <i class="close material-icons" @click="toggleTag(author,'author');search()">close</i>
                      </div>
                    </template>
                    <template v-for="pop in popularTags" :key="pop">
                      <div class="chip"  v-if="pop.active">
                          {{pop.name}}
                          <i class="close material-icons" @click="pop.active = false;search()">close</i>
                      </div>
                    </template>
                </div>
                <div class="col s12">
                    <button type="submit" @click="googleAnalytics('Registry_Searches',query)" class="waves-effect waves-light blue btn">search</button>&nbsp;&nbsp;&nbsp;
                    <a class="blue btn" href="/registry">clear</a>
                </div>
            </form>
            <div class="col s12" id="myAPITipCont">
                <div class="row search-results" id="tippyParentCopy">
                    <div class="col s12" id="tippyParent">
                        <div class="blue-grey-text">
                            <div class="row">
                              <div class="col s5 m10">
                                <template v-if="total && total > 0">
                                  <span class="blue-text p-1" v-text="'Total APIs: '+total"></span>
                                  <CopyButton 
                                  v-if="shareURLButtonVisible" 
                                  @click.prevent="googleAnalytics('Registry_SharedURL', window.location.search );"
                                  copy_msg="URL copied" 
                                  :copy="shareUR">
                                      <template v-slot:title>
                                          Copy Search URL <i class="fa fa-clipboard" aria-hidden="true"></i>
                                      </template>
                                  </CopyButton>
                                </template>
                              </div>
                              <div class="col s5 m2">
                                <select class="browser-default" v-model="sort" @change='search()'>
                                  <option value="" disabled>Sort By</option>
                                  <option value="Relevance" selected>Most Relevant</option>
                                  <option value="Alphabetically A-Z">Alphabetically A-Z</option>
                                  <option value="Alphabetically Z-A">Alphabetically Z-A</option>
                                  <option value="Recently Updated">Recently Updated</option>
                                </select>
                              </div>
                            </div>
                        </div>
                        <template v-if="total == 0">
                          <div class="card">
                            <div class="card-content center">
                              <i class="fa fa-exclamation-circle fa-2x grey-text" aria-hidden="true"></i>
                              <h5 class="grey-text">Your Search Returned No Results</h5>
                            </div>
                          </div>
                        </template>
                        <div class="highlight_container">
                            <template v-for="api in apis" :key="api._id">
                              <RegistryItem :api="api" :total="total" :user="userInfo"></RegistryItem>
                          </template>
                        </div>
                        <div class="row">
                            <div class="col s12 m10 l10">
                              <div class="row">
                                <div class="col s2">
                                  <ul class="pagination">
                                    <li :class="{ disabled: page <= 1 }">
                                        <a href="#" @click.prevent="prevPage(); search()"><i class="material-icons">chevron_left</i> Previous</a>
                                    </li>
                                </ul>
                                </div>
                                <div class="col s8">
                                  <ul class="pagination">
                                    <li :class="{ active: page == n, blue: page == n, 'white-text': page == n  }" v-for="n in pages" :key="n">
                                        <a href="#" @click.prevent="page = n; search()">{{n}}</a>
                                    </li>
                                </ul>
                                </div>
                                <div class="col s2">
                                  <ul class="pagination">
                                    <li :class="{ disabled: page >= pages }">
                                        <a href="#" @click.prevent="nextPage(); search()">Next <i class="material-icons">chevron_right</i></a>
                                    </li>
                                </ul>
                                </div>
                              </div>
                                
                            </div>
                            <div class="col s12 m2 l2 right-align">
                                Per page:
                                <select class="perPage" v-model="perPage" @change="calculatePages; search()" id="perPage">
                                    <option value="10">10</option>
                                    <option value="20">20</option>
                                    <option value="50">50</option>
                                    <option value="100">100</option>
                                </select>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
          </div>
        </div>
        
      </div>
  </div>
</main>
</template>

<script>
import RegistryItem from '../components/RegistryItem.vue';

import tippy from 'tippy.js'
import axios from 'axios'
import Mark from 'mark.js'
import {map, isEmpty, filter} from 'lodash'
import {Collapsible} from 'materialize-css'
import { mapGetters } from 'vuex'


export default {
    name: 'Registry',
    components:{
        RegistryItem
    },
    data: function(){
        return {
            total: Number,
            query: '',
            page: 1,
            pages: 1,
            perPage: 10,
            specialTagsUI: false,
            specialTagName: '',
            specialTagImage: '',
            specialTagURL: '',
            specialTagOriginalName: '',
            shareURL:'',
            shareURLButtonVisible: false,
            sort: 'Relevance',
            loading: false,
            tagsearch:'',
            tagSearchResults:[],
            ownersearch:'',
            ownerSearchResults:[],
            listAll:false,
            listCap:20,
            ownersNotFound: [],
            tagsNotFound: [],
            context: Object,
            popularTags: [],
            tags:Array,
            apis: [],
            authors: [],
            highlighter: null,
            portal_name: ''
        }
      },
      methods: {
          googleAnalytics(category, label){
            // console.log('category',category,label)
            // this.$gtag.event('click',{'event_category':'general','event_label':label,'event_value':1})
            switch (category) {
              case 'Registry_Tag':
                this.$gtag.event('click',{'event_category':'tag','event_label':label,'event_value':1})
                break;
              case 'Registry_Author':
                this.$gtag.event('click',{'event_category':'author','event_label':label,'event_value':1})
                break;
              case 'Registry_APIs':
                this.$gtag.event('click',{'event_category':'expanded','event_label':label,'event_value':1})
                break;
              case 'Registry_SharedURL':
                this.$gtag.event('click',{'event_category':'shared','event_label':label,'event_value':1})
                break;
              case 'Registry_Searches':
                this.$gtag.event('click',{'event_category':'searched','event_label':label,'event_value':1})
                break;
              case 'Registry_Documentation':
                this.$gtag.event('click',{'event_category':'documentation','event_label':label,'event_value':1})
                break;
              default:
              this.$gtag.event('click',{'event_category':'general','event_label':label,'event_value':1})
            }
          },
          mark: function(keyword){
            this.highlighter.unmark();
            this.highlighter.mark(keyword);
          },
          initialAPILoad: function(){
              var self = this;
              let url = "/api/query?"
              self.handleContext(self.context);
              //check for existing query in url string
              self.checkforQuery();
              let query = self.query;
              if(!self.query){
                query="__all__"
              }

              url += "q=" + query
              
              var config = {
                  "params": {
                      'fields': 'info,_meta,_status,paths,tags,openapi,swagger',
                      'size': self.perPage,
                      'from': self.page == 1 ? self.page-1 : ((self.page-1) * self.perPage )  
                  }
              }
              var filters = self.getQueryFilters();
              if (Object.keys(filters).length !== 0){
                for (const param in filters) {
                  url += "&"+param+"="+encodeURIComponent(filters[param])
                }
              }
              self.loading = true;
              axios.get(url, config).then(function(response){
                  self.loading = false;

                  self.apis = response.data.hits;

                  self.total = response.data.total;
                  self.calculatePages();
              }).catch(err=>{
                self.loading = false;
                throw err;
              });
          },
          loadFilters: function (){
              var self = this;
              axios.get('/api/suggestion?field=tags.name').then(function(response){
                  let temp_data = []
                  for(let key in response.data){
                    temp_data.push({key: key, doc_count: response.data[key]})
                  }
                  let tags = map(temp_data, function(item){
                      return {'name':item.key, 'count': item.doc_count, 'active': false};
                  });
                  self.tags = tags;

                  axios.get('/api/suggestion?field=info.contact.name').then(function(response){
                      let temp_data = []
                      for(let key in response.data){
                        temp_data.push({key: key, doc_count: response.data[key]})
                      }
                      let authors = map(temp_data, function(item){
                          return {'name':item.key, 'count': item.doc_count, 'active': false};
                      });

                      self.authors = authors;
                      //When all filters all loaded
                      //share url params depend on filters being loaded
                      self.initialAPILoad();
                  });

              });
          },
          getQueryFilters: function(){
              var tagFilters = [];
              var authorFilters = [];
              var finalFilters = {};
              // regular tags
              this.tags.forEach(function(item){
                if (item.active){
                  tagFilters.push('"'+item.name+'"');
                }   
              });
              // include not found on list
              this.tagsNotFound.forEach(tag => {
                tagFilters.push('"'+tag+'"');
              })
              //popular tags
              this.popularTags.forEach(function(item){
              if (item.active && !tagFilters.includes(item.name))
                tagFilters.push('"'+item.name+'"');
              });

              if (tagFilters.length > 0){
                finalFilters['tags'] = tagFilters;
              }

              this.authors.forEach(function(item){
                if (item.active){
                  authorFilters.push('"'+item.name+'"');
                }
              });
              // include not found on list
              this.ownersNotFound.forEach(owner => {
                authorFilters.push('"'+owner+'"');
              })
              if (authorFilters.length){
                finalFilters['authors'] = authorFilters;
              }
              // console.log('filters found', finalFilters)
              return finalFilters;
          },
          searchForTags: function(tagName){
            var self = this;
            for (var i = 0; i < self.tags.length; i++) {
              if (self.tags[i].name === tagName) {
                self.tags[i].active = !self.tags[i].active;
                self.search();
              }
              else{
                self.search();
              }
            }
          },
          buildShareURL: function(q){
            var filters = [];
            var authorFilters = [];
            var finalFilters = '';
            var finalAuthorFilters ='';
            var finalURL = window.location.origin+window.location.pathname;
            // Collect TAGS
            this.tags.forEach(function(item){
              if (item.active)
                  filters.push(item.name);
              });
            // Collect Owners
            this.authors.forEach(function(item){
              if (item.active){
                authorFilters.push(item.name);
              }
            });
            //Detect QUERY
            if (q !== '__all__') {
              finalURL = finalURL+'?q='+q;
              //if any tags are actuve
              if(authorFilters.length || filters.length){
                finalURL = finalURL+"&";
              }
            }
            //if tags active but no query
            else if(authorFilters.length || filters.length){
              finalURL = finalURL+"?";
            }
            // if BOTH filters exists
            if (filters.length && authorFilters.length) {
              finalFilters = filters.join(',')
              finalURL = finalURL+"tags="+finalFilters;

              finalAuthorFilters = authorFilters.join(',')
              finalURL = finalURL+"&owners="+finalAuthorFilters;
            }
            // if Owners Exist but no Tags
            else if (!filters.length && authorFilters.length) {
              finalAuthorFilters = authorFilters.join(',')
              finalURL = finalURL+"owners="+finalAuthorFilters;
            }
            // if Tags exists but no owners
            else if (filters.length && !authorFilters.length) {
              finalFilters = filters.join(',')
              finalURL = finalURL+"tags="+finalFilters;
            }

            this.shareURL =finalURL;
            //HTML5 change url history
            window.history.pushState({"html":'content',"pageTitle":'SmartAPI'},"", finalURL);
            this.shareURLButtonVisible = true;
          },
          search: function () {
              var self = this;
              let url = '/api/query?'
              let query = self.query.trim();
              // reset results
              self.apis = [];
              self.total = 0;
              //unmark keywords
              self.highlighter.unmark();

              if (!self.context.Special && !query){
                query = "__all__";
              }
              else if (self.context.Special && !query) {
                query = query || "__all__";
                // self.handleSpecialTags(self.context.Tags[0]);
              }
              if (query) {

                  self.googleAnalytics('Registry_Searches',query)

                  url += "q=" + query

                  var config = {
                      "params": {
                          'fields': 'info,_meta,_status,paths,tags,openapi,swagger',
                          'size': self.perPage,
                          'from': self.page == 1 ? self.page-1 : ((self.page-1) * self.perPage )          
                      },
                  };
                  var filters = this.getQueryFilters();
                  if (Object.keys(filters).length !== 0){
                    for (const param in filters) {
                      url += "&"+param+"="+encodeURIComponent(filters[param])
                    }
                  }
                  self.loading = true;
                  // Share search URL
                  self.buildShareURL(query);

                  // sort
                  switch (self.sort) {
                    case 'Relevance':
                      //default behavior
                      break;
                    case 'Alphabetically A-Z':
                      url = url+'&sort=info.title.raw'
                      break;
                    case 'Alphabetically Z-A':
                      url = url+'&sort=-info.title.raw'
                      break;
                    case 'Recently Updated':
                      url = url+'&sort=_meta.last_updated'
                      break;
                    default:
                      //no matching sort
                      break;
                  }
                  axios.get(url, config).then(function (response) {
                      self.loading = false;
                      self.highlighter.unmark();
                      self.apis = response.data.hits;
                      // self.handleContext(self.context);
                      self.total = response.data.total;
                      self.calculatePages();
                  }).catch(err=>{
                    self.loading = false;
                    throw err;
                  });
              }
          },
          calculatePages: function () {
              this.pages = Math.ceil(this.total / this.perPage);
              // console.log("____________")
              // console.log('total', this.total)
              // console.log('per page', this.perPage)
              // console.log('pages', this.pages)
              if(this.page > this.pages){
                this.page = 1
              }
          },
          prevPage: function () {
              if (this.page > 1)
                  this.page -= 1
          },
          nextPage: function () {
              if (this.page < this.pages)
                  this.page += 1
          },
          handleRegularTags: function(rTags){
            var self = this;
              self.specialUI = false;
              for (var i = 0; i < rTags.length; i++) {
                for (var x = 0; x < self.tags.length; x++) {
                  if (rTags[i].toLowerCase() === self.tags[x].name.toLowerCase()) {
                    self.toggleThisTag(self.tags[x])
                  }
                }
              }
          },
          handleOwnerTags: function(rTags){
            var self = this;
              self.specialUI = false;
              for (var i = 0; i < rTags.length; i++) {
                for (var x = 0; x < self.authors.length; x++) {
                  if (rTags[i].toLowerCase() === self.authors[x].name.toLowerCase()) {
                    self.toggleThisAuthor(self.authors[x])
                  }
                }
              }
          },
          handleContext: function(context){
            if (context.Special) {
              this.handleSpecialTags(this.context.Tags[0]);
            }
            if (!context.Special && !isEmpty(context.Tags)) {
              this.handleRegularTags(this.context.Tags);
            }
            if (!context.Special &&  !isEmpty(context.Owners)) {
              this.handleOwnerTags(this.context.Owners);
            }
          },
          handleSpecialTags: function(tagname){
            var self = this;
              self.specialTagsUI = true;
              self.specialTagOriginalName = tagname.toUpperCase();
              switch (tagname) {
                case 'translator':
                  self.specialTagName = 'NCATS Biomedical Data Translator';
                  self.specialTagImage = 'TranslatorLogo.jpg';
                  self.specialTagURL = 'https://ncats.nih.gov/translator';
                  break;
                  case 'nihdatacommons' || 'NIHdatacommons':
                    self.specialTagName = 'NIH Data Commons';
                    self.specialTagImage = 'nih-logo.png';
                    self.specialTagURL = 'https://commonfund.nih.gov/commons';
                    break;
                default:
                  self.specialTagName = tagname.toUpperCase();
                  self.specialTagImage = 'logo-small.png';
                  self.specialTagURL = 'https://smart-api.info';
              }
              for (var i = 0; i < self.tags.length; i++) {
                if (self.tags[i].name.toLowerCase() === tagname.toLowerCase()) {
                  self.tags[i]['active'] = true
                 }
              }            
          },
          checkforQuery: function(){
            var self = this;
            var url_string = window.location.href
            var url = new URL(url_string);

            var q = url.searchParams.get("q");
            if (q) {
              this.query = q;
            }

            var tags = url.searchParams.get("tags");
            // console.log('TAGS FOUND',tags)
            if (tags) {
              if (tags.includes(',')) {
                tags = tags.split(',')
              }else {
                tags = [tags]
              }
              for (var i = 0; i < tags.length; i++) {
                for (var x = 0; x < self.tags.length; x++) {
                  if (self.tags[x].name === tags[i]) {
                    self.tags[x]['active'] = true
                    tags.splice(i, 1)
                  }
                }
              }
            }
            if (tags && tags.length){
              self.tagsNotFound = tags
              console.warn('TAGS NOT FOUND', self.tagsNotFound)
            }

            var owners = url.searchParams.get("owners");
            if (owners) {
              if (owners.includes(',')) {
                owners = owners.split(',')
              }else {
                owners = [owners]
              }
              for (var j = 0; j < owners.length; j++) {
                for (var xx = 0; xx < self.authors.length; xx++) {
                  if (self.authors[xx].name === owners[j]) {
                    owners.splice(j, 1)
                    self.tags[i]['active'] = true

                  }
                }
              }
            }
            if (owners && owners.length){   
              self.ownersNotFound = owners
              console.warn('OWNERS NOT FOUND', self.ownersNotFound)
            }

            if (!owners && !tags){
              self.ownersNotFound = []
              self.tagsNotFound = []
            }

          },
          getAnalytics(){
            var self = this;
            axios.get('https://gasuperproxy-1470690417190.appspot.com/query?id=ahxzfmdhc3VwZXJwcm94eS0xNDcwNjkwNDE3MTkwchULEghBcGlRdWVyeRiAgIDMgsmRCgw').then(res=>{
              if (res.data.rows) {
                let analytics = res.data.rows;
                let pop = []
                for (var i = 0; i < analytics.length; i++) {
                  if (analytics[i][0] ==='tag') {
                    let name = analytics[i][1];
                    if(!name.includes(' ')){
                      pop.push({'name':name,'active':false,'count':analytics[i][2],'type':'tags'})
                    }else{
                      pop.push({'name':name,'active':false,'count':analytics[i][2],'type':'owners'})
                    }
                  }
                }
                self.popularTags = pop;
              }

            }).catch(err=>{
              throw err;
            });
          },
          toggleTag(tag,type){
            let self = this;
            switch (type) {
              case 'author':
                self.toggleThisAuthor(tag)
                break;
              case 'tag':
                self.toggleThisTag(tag)
                break;
              default:
                return false
            }
          },
          toggleThisTag(tag){
            let self = this;
            for (var i = 0; i < self.tags.length; i++) {
                if (self.tags[i].name === tag.name) {
                    self.tags[i]['active'] = !self.tags[i]['active']
                }
              }
          },
          toggleThisAuthor(author){
            let self = this;
            for (var i = 0; i < self.authors.length; i++) {
              if (self.authors[i].name === author.name) {
                self.authors[i]['active'] = !self.authors[i]['active']
              }
            }
          },
      },
      created: function () {
            this.loadFilters();
            this.getAnalytics();
            this.$gtag.customMap({ 'dimension5': 'registryResults' })
            this.$gtag.customMap({ 'metric1': 'registry-item' })
      },
      mounted: function(){
        var self = this;

        var elems = document.querySelectorAll('.collapsible');
        Collapsible.init(elems);

        if (Object.prototype.hasOwnProperty.call(self.$route.params, 'portal_name')) {
            self.portal_name = self.$route.params['portal_name'].toLowerCase()
            self.context = {
                'Special': true,
                'Tags': [self.portal_name]
            }
          }

        self.highlighter = new Mark(document.querySelector(".highlight_container"))

        window.onpopstate = function() {
          self.initialAPILoad();
        };
        
        /*eslint-disable */
        tippy('.tipped',{
              placement: 'top',
              theme:'light',
              interactive:true,
              onShow(instance) {
                let status = instance.reference.dataset.tippyStatus;
                let msg = [200, 299, '200', '299'].includes(status) ? 'This API belongs to you. Manage it on your <a href="/dashboard">dashboard</a>.' : '<b class="red-text">API metadata cannot be synchronized with its source URL due to an error.</b> <br>Fix the issue and refresh it from your <a href="/dashboard">dashboard</a>.'
                instance.setContent("<div class='p-1 blue-text left-align'>"+msg+"</div>")
              },
            });
        /*eslint-enable */
      },
      updated: function(){
        // Highlight matches in results
        this.mark(this.query);
      },
      watch:{
        tagsearch:function(q){
          var self = this;

          if (q.length) {
            let result = filter(self.tags, function(o) {
                if (o['name'].toLowerCase().includes(q.toLowerCase())) {
                  return o;
                }
            });
            self.tagSearchResults = result;
          }else {
            this.tagSearchResults = [];
          }

        },
        ownersearch:function(q){
          var self = this;

          if (q.length) {
            let result = filter(self.authors, function(o) {
                if (o['name'].toLowerCase().includes(q.toLowerCase())) {
                  return o;
                }
            });
            self.ownerSearchResults = result;
          }else {
            this.ownerSearchResults = [];
          }

        },
        listAll:function(b){
          var self = this;
          if (b) {
            self.listCap = 1000;
          }else {
            self.listCap = 20;
          }
        },
      },
      computed:{
            ...mapGetters([
                'loggedIn',
                'userInfo'
            ])
        },
}
</script>

<style lang="css">
    mark{
        background-color: transparent;
        color: rgb(255, 71, 71);
    }
</style>