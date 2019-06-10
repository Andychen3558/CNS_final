'''
#Use like this!!:
from server_core import API
users = API()

user_name = 'A-di'
password = 'English'
sessionid = 77777

#registeration
susess = users.register(password)
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
    def __init__(self, vecfile, cache=None):
        self.model = Embedding.Embedding(vecfile, cache)
        self.Record={}  ## { (username, sessionid): {'try_times' : ??, 'score' : ?? , 'NowQuestion': ??, 'time' :?? ,'success': True/False } }
        
        ## use for score threshold
        self.success_thres = 0.6
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
            if self.Record[conn]['time']+self.timeout < now_time:
                self._remove_dead_connection(conn)
        return
    
    def _get_list(self, now):
        return [attr['name'] for attr in self.Record[now]['NowQuestion'].values()], [attr['url'] for attr in self.Record[now]['NowQuestion'].values()]

    def _check(self, now):     
        ## success if score is enough
        if self.Record[now]['score']>self.success_thres:
            self.Record[now]['success'] = True
        
        ## failure if times exceed
        elif self.Record[now]['try_times']> self.try_bound:
            self.Record[now]['failure'] = True
        
        return   
        
    ## return (True, None) <- success,
    ##    (True, a list contain nine object) <- during authorization ,
    ##    (False, None) <- fail 
    def try_to_login(self, username, password, sessionid):
        ##new session
        now = ( username, sessionid )
        
        if self.Record.get( now )==None:
            ## initialize 
            newQuestion = dict(self.model.get_options(password, get_url=True))
            self.Record[now]= {'try_times'   : 0,
                               'score'     : 0,
                               'NowQuestion' : newQuestion,
                               'time'      : int(time.time()),
                               'success': False,
                               'failure': False}
        
        self._check(now)
        
        if self.Record[now]['success']==True:
            return (True, None, None)
        elif self.Record[now]['failure']==True:
            self._remove_dead_connection(now)
            return (False, None, None)
        else:
            print (self.Record[now]['NowQuestion'])
            tmp_list, tmp_list2 = self._get_list(now)
            print (tmp_list, tmp_list2)
            return (True, tmp_list, tmp_list2)
        
        
        

    ## No return value
    def update_by_choice(self, username, password, sessionid, user_ans):
        now = (username, sessionid)
        if self.Record.get(now) == None:
            print('You are caculating a score in a nonexistent session.')
            print('diggerrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr!!!!!')
        else:
            now_question = self.Record[now]['NowQuestion']

            word=None

            # print ("user_ans is: ", user_ans)

            for tmp in now_question.keys():
                print(tmp, now_question[tmp]['score'])
                if now_question[tmp]['name'] == user_ans:
                    word = tmp
            if word==None:
                return
            '''
            bias = sum([attr['score'] for attr in now_question.values()]) / len(now_question)
            
            chosen_score = now_question[ word ]['score']
            ## penalize low-scored choices
            if chosen_score < bias:
                self.Record[now]['score'] = float('-inf')
            else:
                self.Record[now]['score'] += chosen_score
            '''

            score_list = [attr['score'] for attr in now_question.values()]
            max_score, min_score = max(score_list), min(score_list)
            chosen_score = now_question[ word ]['score']
            now_times = self.Record[now]['try_times']
            #self.Record[now]['score'] *= now_times
            self.Record[now]['score'] += (chosen_score - min_score) / (max_score - min_score) / (self.try_bound + 1)
            #self.Record[now]['score'] /= now_times + 1


            # print ( "score is: " , self.Record[now]['score'] )
            new_question = dict(self.model.get_options(password, get_url=True))
            self.Record[now]['NowQuestion'] = new_question
            self.Record[now]['try_times'] += 1
            self.Record[now]['time'] = int(time.time())

        return
    
    # return a string that an attacker may choose
    
    def attack(self, username, sessionid, history):
        now = (username, sessionid)
        now_question = self.Record[now]['NowQuestion']
        guessed_ans = None
        max_score = float('-inf')
        for name in now_question.keys():
            score = 0
            for his in history:
                score += self.model.similarity(name, his)
            if score > max_score:
                guessed_ans = name
                max_score = score
        return guessed_ans
    
    def _compare_list(self, list1, list2):
        if len(list1)!=len(list2):
            return False
        for i in range(len(list1)):
            if list1[i]!=list2[i]:
                return False
        return True
    
    ## return [ [ word 1 , word 2, ...], ... ]
    def _get_list_v2(self, now): 
        return [ [ attr['name'] for attr in tmp_list] for tmp_list in self.Record[now]['NowQuestion'] ], [ [ attr['url'] for attr in tmp_list] for tmp_list in self.Record[now]['NowQuestion'] ]
        
    
    def try_to_login_v2(self, username, password, sessionid):
        ##new session
        now = ( username, sessionid )
        
        if self.Record.get( now )==None:
            ## initialize 
            ## list , list , dict
            newQuestion = list(self.model.get_options_by_size(password,5,3, get_url=False))
            
            self.Record[now]= {'try_times'   : 0,
                               'score'     : 0,
                               'NowQuestion' : newQuestion,
                               'time'      : int(time.time()),
                               'success': False,
                               'failure': False}
        
        self._check(now)
        
        if self.Record[now]['success']==True:
            return (True, None, None)
        elif self.Record[now]['failure']==True:
            self._remove_dead_connection(now)
            return (False, None, None)
        else:
            tmp_list, tmp_list2 = self._get_list_v2(now)
            return (True, tmp_list, tmp_list2)
    
    ## No return value
    def update_by_choice_v2(self, username, password, sessionid, user_ans):
        now = (username, sessionid)
        if self.Record.get(now) == None:
            print('You are caculating a score in a nonexistent session.')
            print('diggerrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr!!!!!')
        else:
            now_question = self.Record[now]['NowQuestion']

            word_list=None

            # print ("user_ans is: ", user_ans)

            for tmp_list in now_question:
                tmp_list2 = [ attr['name'] for attr in tmp_list ]
                # print (tmp_list2)
                # print(user_ans)
                if self._compare_list(tmp_list2 , user_ans)== True:

                    word_list = tmp_list
            # print(word_list)
            if word_list==None:
                return
            
    
            score_list = [ max ([attr['score'] for attr in tmp_list ]) for tmp_list in now_question ]
            max_score, min_score = max(score_list), min(score_list)
            chosen_score = max([ attr['score'] for attr in word_list ])
            print(score_list, chosen_score)        
            now_times = self.Record[now]['try_times']
            #self.Record[now]['score'] *= now_times
            self.Record[now]['score'] += (chosen_score - min_score) / (max_score - min_score) / (self.try_bound + 1)
            #self.Record[now]['score'] /= now_times + 1


            # print ( "score is: " , self.Record[now]['score'] )
            new_question = list(self.model.get_options_by_size(password,5,3, get_url=False))
            # print(new_question)
            self.Record[now]['NowQuestion'] = new_question
            self.Record[now]['try_times'] += 1
            self.Record[now]['time'] = int(time.time())

        return
    
    # return a list of string that an attacker may choose
    def attack_v2(self, username, sessionid, history):
        now = (username, sessionid)
        now_question = self.Record[now]['NowQuestion']
        guessed_ans = None
        max_score = float('-inf')
        for group in now_question.values():
            group_names = [attr['name'] for attr in group]
            score = 0
            for his_names in history:
                score += max([self.model.similarity(group_name, his_name)
                              for group_name, his_name in zip(group_names, his_names)])
            if score > max_score:
                guessed_ans = group_names
                max_score = score
        return guessed_ans
    
