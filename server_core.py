'''
#Use like this!!:
from server_core import API
users = API()

user_name = 'A-di'
password = 'English'
sessionid = 77777

#registeration
susess = users.register(username, password, sessionid)
if sucess:
    print('you is good oh!')
else:
    print('you failed to sign in!')

#login
good , next_question = user.try_to_login(username, password, sessionid)
while good and next_question is not None:
    #user choose an answer from next_question
    user.update_by_choice(username, password, sessionid, user_ans)
    good , next_question = user.try_to_login(username, password, sessionid)
if not good:
    print('login failed.')
else:
    print('login sucessed.')
'''

from embedding import Embedding
import time

class API():
    def __init__():
        self.vecfile = 'embedding/wiki.zh.vec.small'
        self.model = Embedding.Embedding(self.vecfile)
        self.Record={}  ## { (username, sessionid): {'try_times' : ??, 'score' : ?? , 'NowQuestion': ??, 'time' :?? ,'success': True/False } }
        
        ## use for score threshold
        self.success_thres = 1 
        self.try_bound = 3
        
        ## use for timeout
        self.timeout = 120
        
    ## return True if password ,False else
    def register(self, password):
        return self.model.invocab(password)
    
    ## remove self.Record failure member
    def _remove_dead_connection(self, now):
        del self.Record[now]
        return
    
    def remove_timeout(self):
        now_time = int(time.time())
        for conn in self.Record.keys():
            if self.Record[conn]['time']+self.timeout < now_time
                self._remove_dead_connection(conn)
        return
    
    def _get_list(self, now):
        return [attr['name'] for attr in self.Record[now]['NowQuestion'].values()]
        #return [attr['url'] for attr in self.Record[now]['NowQuestion'].values()]

    def _check(self, now):       
        ## success if score is enough
        if self.Record[now]['score']>self.success_thres:
            self.Record[now]['success'] = True
        
        ## failure if times exceed
        elif self.Record[now]['try_times']> self.try_bound:
            self.Record[now]['failure'] = True
        
        return     
        
    ## return (True, None) <- success,
    ##        (True, a list contain nine object) <- during authorization ,
    ##        (False, None) <- fail 
    def try_to_login(self, username, password, sessionid):
        ##new session
        now = ( username, sessionid )
        
        if self.Record.get( now )==None:
            ## initialize 
            newQuestion = model.get_options(password)
            self.Record[now]= {'try_times'   : 0,
                               'score'       : 0,
                               'NowQuestion' : newQuestion,
                               'time'        : int(time.time()),
                               'success': False,
                               'failure': False}
        
        self._check(now)
        
        if self.Record[now]['success']==True:
            return (True, None)
        elif self.Record[now]['failure']==True:
            _remove_dead_connection(now)
            return (False, None)
        else:
            tmp_list = self._get_list(now)
            return (True, tmp_list)
        
        
        

    ## No return value
    def update_by_choice(self, username, password, sessionid, user_ans):
        now = (username, sessionid)
        if self.Record.get(now) == None:
            print('You are caculating a score in a nonexistent session.')
            print('diggerrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr!!!!!')
        else:
            now_question = self.Record[now]['NowQuestion']
            bias = sum([attr['score'] for attr in now_question.values()]) / len(now_question)
            if now_question.get(user_ans) == None:
                return
            chosen_score = now_question[user_ans]['score']
            ## penalize low-scored choices
            if chosen_score < bias:
                self.Record[now]['score'] = float('-inf')
            else:
                self.Record[now]['score'] += chosen_score
            new_uestion = model.get_options(password)
            self.Record[now]['NowQuestion'] = new_question
            self.Record[now]['try_times'] += 1
            self.Record[now]['time'] = int(time.time())

        return
