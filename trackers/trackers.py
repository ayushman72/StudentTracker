import matplotlib.pyplot as plt

class Tracker():
    
    def __init__(self,quiz):
        self.score = [quiz['score']]
        self.accuracy = [self.__parse_accuracy(quiz['accuracy'])]
        self.speed = [int(quiz['speed'])]
        self.correct = [quiz['correct_answers']]
        self.incorrect = [quiz['incorrect_answers']]
        self.better_than = [quiz['better_than']]
        self.mistakes_corrected = [quiz['mistakes_corrected']]
        self.initial_mistakes = [quiz['initial_mistake_count']]
    
  
    def __parse_accuracy(self,str_acc:str):
        rem_per = str_acc.split("%")[0].strip()
        return int(rem_per)
        
    def add_data(self,quiz):
        self.score.append(quiz['score'])
        self.accuracy.append(self.__parse_accuracy(quiz['accuracy']))
        self.speed.append(int(quiz['speed']))
        self.correct.append(quiz['correct_answers'])
        self.incorrect.append(quiz['incorrect_answers'])
        self.better_than.append(quiz['better_than'])
        self.mistakes_corrected.append(quiz['mistakes_corrected'])
        self.initial_mistakes.append(quiz['initial_mistake_count'])
        
    def __len__(self):
        return len(self.score)
    
    def __getitem__(self,idx):
        ret_dict = {}
        for k,v in self.__dict__.items():
            if isinstance(v,list):
                ret_dict[k] = v[idx]
        return ret_dict
    
    
    def average_stats(self,span = -1):
        assert ((span == -1) or (span > 0)), 'only -1 or +ve numbers allowed'
        assert (len(self) > 0), 'there is no prior data'
        if span == -1:
            span = len(self)
        avg_dict = {}
        for k,v in self.__dict__.items():
            if k == "quiz_id":
                continue
            elif k == 'accuracy':
                avg_dict[k] = int(100*sum(self.correct[-span:])/(sum(self.correct[-span:])+sum(self.incorrect[-span:])))
            elif isinstance(v,list) and isinstance(v[0],(int,float)):
                avg_dict[k] = sum(v[-span:])/span
        return avg_dict
    
    @staticmethod
    def parse_quiz(quiz:dict):
        
        def __parse_accuracy(str_acc:str):
            rem_per = str_acc.split("%")[0].strip()
            return int(rem_per)
        
        records = {}
        records["score"] = quiz['score']
        records["accuracy"] = __parse_accuracy(quiz['accuracy'])
        records["speed"] = int(quiz['speed'])
        records["correct"] = quiz['correct_answers']
        records["incorrect"] = quiz['incorrect_answers']
        records["better_than"] = quiz['better_than']
        records["mistakes_corrected"] = quiz['mistakes_corrected']
        records["initial_mistakes"] = quiz['initial_mistake_count']
        records['topic'] = quiz['quiz']['topic'].lower().strip()
        
        return records
    
    

class QuizTracker(Tracker):
    def __init__(self,quiz):
        self.quiz_id = quiz['quiz_id']
        self.quiz_name = quiz['quiz']['title']
        
        super().__init__(quiz)
        
    def __hash__(self):
        return hash(self.quiz_id)
    
    
    def __repr__(self):
        return f"Quiz with ID: {self.quiz_id} and name `{self.quiz_name}`"
    
    def retook(self,quiz):
        assert self.quiz_id == quiz['quiz_id'],"only same quiz can be added in this"
        self.add_data(quiz)
        
    def latest(self):
        return self[-1]
    
    def compare_from_past(self,quiz):
        
        if len(self) == 0:
            print('No data to compare to')
            return
        
        avg_stat = self.average_stats()
        # last = self.latest()
        current = Tracker.parse_quiz(quiz)
        
        checks = ['score','accuracy','speed','better_than']
        
        for check in checks:
            plt.title(check.capitalize())
            plt.plot(self.__dict__[check],marker = 'o', label = "History")
            plt.plot([avg_stat[check]]*len(self),linestyle = '--', label = "Average")
            plt.plot([current[check]]*len(self), label = "Current")
            plt.xticks(visible = False)
            plt.legend()
            plt.show()
            
    def look(self):
        if len(self) == 0:
            print('No data to compare to')
            return
        
        avg_stat = self.average_stats()
        
        checks = ['score','accuracy','speed','better_than']
        
        for check in checks:
            plt.title(check.capitalize())
            plt.plot(self.__dict__[check],marker = 'o', label = "History")
            plt.plot([avg_stat[check]]*len(self),linestyle = '--', label = "Average")
            plt.xticks(visible = False)
            plt.legend()
            plt.show()
            
        
class TopicTracker(Tracker):
    def __init__(self,quiz):
        self.topic = quiz['quiz']['topic'].lower().strip()
        self.quiz_id = [quiz['quiz_id']]
        self.quiz_trackers = {quiz['quiz_id'] : QuizTracker(quiz)}
        super().__init__(quiz)
        
    def __hash__(self):
        return hash(self.topic)
    
    def __repr__(self):
        return f"Topic with name `{self.topic}` with quizes: {self.show_quizes()}"
    
    def get_quiz(self, quiz_id):
        return self.quiz_trackers[quiz_id]
    
    def show_quizes(self):
        return list(self.quiz_trackers.keys())
    
    def retook(self,quiz):
        assert self.topic == quiz['quiz']['topic'].lower().strip(),\
            "only same topic can be added in this"
        
        if quiz['quiz_id'] not in self.quiz_trackers:
            self.quiz_trackers[quiz['quiz_id']] = QuizTracker(quiz)
        else:
            self.quiz_trackers[quiz['quiz_id']].retook(quiz)
        
        self.quiz_id.append(quiz['quiz_id'])
        self.add_data(quiz)
        
    def latest(self):
        return self[-1]
    
    def compare_from_past(self,quiz):
        
        if len(self) == 0:
            print('No data to compare to')
            return
        
        avg_stat = self.average_stats()
        last = self.latest()
        current = Tracker.parse_quiz(quiz)
        
        checks = ['accuracy','score','speed','better_than']
        
        for check in checks:
            plt.suptitle(check.capitalize())
            plt.plot(self.__dict__[check],marker = 'o', label = "History")
            plt.plot([avg_stat[check]]*len(self),linestyle = '--', label = "Average")
            plt.plot([current[check]]*len(self), label = "Current")
            
            if current[check] > avg_stat[check]:
                if current[check] > last[check]:
                    sub = f"Your {check} is increasing. "
                else:
                    sub = f'You did better than average. '
                    
            elif current[check] == avg_stat[check]:
                sub = f"You are consistent"
            else:
                if current[check] > last[check]:
                    sub = f'Your {check} increased but more work is needed.'
                else:
                    sub = f'OH no, hard work is needed '
                    
            plt.title(sub)
            plt.xticks(visible = False)
            plt.legend()
            plt.show()
    
         
    def look(self):
        if len(self) == 0:
            print('No data to compare to')
            return
        
        avg_stat = self.average_stats()
        
        checks = ['score','accuracy','speed','better_than']
        
        for check in checks:
            plt.title(check.capitalize())
            plt.plot(self.__dict__[check],marker = 'o', label = "History")
            plt.plot([avg_stat[check]]*len(self),linestyle = '--', label = "Average")
            plt.xticks(visible = False)
            plt.legend()
            plt.show()
            

class MassTracker():
    
    def __init__(self,quizes:dict) -> None :
        self.topic_taken:dict[str,TopicTracker] = {}
        for quiz in reversed(quizes):
            if (name:=quiz['quiz']['topic'].lower().strip()) not in self.topic_taken:
                self.topic_taken[name] = TopicTracker(quiz)
            else:
                self.topic_taken[name].retook(quiz)
                
    def __getitem__(self,name):
        return self.topic_taken[name]
        
    def __repr__(self):
        return f"MassTracker with topics {self.show_topics()}"
    
    def show_topics(self):
        return list(self.topic_taken.keys())
    
    def add_quiz(self,quiz):
        if (name:=quiz['quiz']['topic'].lower().strip()) not in self.topic_taken:
            self.topic_taken[name] = TopicTracker(quiz)
        else:
            self.topic_taken[name].retook(quiz)        
    
    def compare_from_past(self,quiz):
        if (name:=quiz['quiz']['topic'].lower().strip()) not in self.topic_taken:
            print('This is the first quiz under the topic ',name,'. Hence can not compare')
        else:
            self.topic_taken[name].compare_from_past(quiz)
    
    def SWOTAnalysis(self) -> dict[str,list[str]]:
        strength:list[str] = []
        weakness:list[str] = []
        opportunity:list[str] = []
        threat:list[str] = []
        
        TWOS = [threat,weakness,opportunity,strength]
        TWOS_name = ['threat','weakness','opportunity','strength']
        
        suggestions:list[str] = []
        

        
        def insert(metric,type,name):
            TWOS[type].append(f"Your {metric} in `{name}` is a {TWOS_name[type]}")
        
        
        for name,topic in self.topic_taken.items():
            support = 0
            stats = topic.average_stats()     
            
              
            # 30% or less accuracy is threat and the classification jumps every 20% 
            type = max(0,   int((stats['accuracy']-31)//20))
            insert('accuracy',type,name)
            support += type
            
            # speed less than 66 is threat abd classification jumps every 15 
            type = max(0,   int((stats['speed']-66)//15))
            insert('speed',type,name)
            support += type
            
            
            per_initial_mistake = 100*stats['initial_mistakes']//(stats['correct'] + stats['incorrect'])
            per_corrected = 100*stats['mistakes_corrected']//stats['initial_mistakes']
            
            if per_initial_mistake <= 10:
                support += 3
                strength.append(f'You answer more than 90% of `{name}` related questions correctly in the first try')
            elif per_initial_mistake <= 25:
                if per_corrected >= 50:
                    support += 3
                else:
                    support += 2
                suggestions.append(f'You seem a bit confused in the topic `{name}`.')
                
            elif per_initial_mistake<=40:
                support += 1
                weakness.append(f'You tend to answer `{name}` related question wrong in the first try')
                if per_corrected > 50:
                    weakness[-1] += " but you correct it after some thinking."
            
            else:
                threat.append(f'You wrongly answer most of the question in `{name}` at first')
                
                
            type = int(support//3)
            TWOS[type].append(f'Overall `{name}` is your {TWOS_name[type]}')
            if type<2:
                suggestions.append(f'You need to study `{name}` more')
            
        return {"S":strength,'W':weakness,'O':opportunity,'T':threat,'suggestions':suggestions}  
    
    
    def SWOTImage(self,output_path: None|str = None):
        fig,axes = plt.subplots(2,2,figsize = (12,8),facecolor = 'black')
        fig.suptitle('SWOT Analysis',fontsize = 20, fontweight = 'bold',color = 'white')
        
        swot_data = self.SWOTAnalysis()
        
        #SWOT data
        swot_mapping = {'Strengths':(0,0),'Weaknesses':(0,1),"Oportunities":(1,0),"Threats":(1,1)}
        colors = {"Strengths":'#4CAF50','Weaknesses':'#F44336',"Oportunities":"#2196F3",'Threats':'#FF9800'}
        
        for category,(row,col) in swot_mapping.items():
            ax = axes[row,col]
            ax.set_title(category,fontsize = 16,color = colors[category])
            ax.axis('off')
            sentences = '\n'.join(f"- {s}" for s in swot_data[category[0]])
            ax.text(0.5,0.5,sentences,fontsize = 12,ha='center',va='center',wrap = True,color = 'white')
    
            
        plt.tight_layout(rect=(0,0,1,0.95))
        if output_path:
            plt.savefig('SWOT_'+output_path)
        
        plt.show()
        
        #Suggestion
        plt.figure(figsize=(8,5), facecolor='black')
        plt.title('Suggesetions',fontsize = 20, fontweight = 'bold', color = 'white')
        sentences = '\n'.join(f"- {s}" for s in swot_data['suggestions'])
        plt.axis('off')
        plt.text(0.5,0.5,sentences,fontsize = 12,ha='center',va='center',wrap = True,color = 'white')
        plt.tight_layout()
        if output_path:
            plt.savefig('Suggestion_'+output_path)
        plt.show()
                
        
    
                          
            