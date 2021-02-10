# from utils.data import SmartAPIData


# class GitWebhookHandler(BaseHandler):

#     data_handler = SmartAPIData()

#     def post(self):
#         # do message authentication
#         digest_obj = hmac.new(key=self.web_settings.API_KEY.encode(
#         ), msg=self.request.body, digestmod=hashlib.sha1)
#         if not hmac.compare_digest('sha1=' + digest_obj.hexdigest(), self.request.headers.get('X-Hub-Signature', '')):
#             self.set_status(405)
#             self.finish({'success': False, 'error': 'Invalid authentication'})
#             return
#         data = tornado.escape.json_decode(self.request.body)
#         # get repository owner name
#         repo_owner = data.get('repository', {}).get(
#             'owner', {}).get('name', None)
#         if not repo_owner:
#             self.set_status(405)
#             self.finish({'success': False, 'error': 'Cannot get repository owner'})
#             return
#         # get repo name
#         repo_name = data.get('repository', {}).get('name', None)
#         if not repo_name:
#             self.set_status(405)
#             self.finish({'success': False, 'error': 'Cannot get repository name'})
#             return
#         # find all modified files in all commits
#         modified_files = set()
#         for commit_obj in data.get('commits', []):
#             for fi in commit_obj.get('added', []):
#                 modified_files.add(fi)
#             for fi in commit_obj.get('modified', []):
#                 modified_files.add(fi)
#         # build query
#         _query = {"query": {"bool": {"should": [
#             {"regexp": {"_meta.url.raw": {"value": '.*{owner}/{repo}/.*/{fi}'.format(owner=re.escape(repo_owner), repo=re.escape(repo_name), fi=re.escape(fi)),
#                                           "max_determinized_states": 200000}}} for fi in modified_files]}}}

#         # get list of ids that need to be refreshed
#         ids_refresh = [x['_id'] for x in self.data_handler.fetch_all(query=_query)]
#         # if there are any ids to refresh, do it
#         if ids_refresh:
#             self.data_handler.refresh_all(id_list=ids_refresh, dryrun=False)
