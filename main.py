# A very simple Flask Hello World app for you to get started with...
import vk_api, random, json
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboardColor,VkKeyboard
import requests
# from flask import Flask
#
# app = Flask(__name__)

admin_panel = {}

class groupClass():
    def __init__(self, token):
        self.token = token
        self.session = vk_api.VkApi(token=self.token)
        self.api = self.session.get_api()
        self.longpoll = VkBotLongPoll(self.session, 186270205)

    def getGroupIndex(self,groupdid):
        try:
            data = json.load(open('base.json',encoding='utf-8'))
        except:
            return -1
        for index in range(len(data)):
            if data[index]['GROUP_ID'] == groupdid:
                return index
        return -1

    def getTemplate(self,groupid):
        return {'GROUP_ID':groupid,'ADMINS':[],'VIPS':[],'Users':{},'Options':{'AutoKick':0,'Greeting':'Приветствую вас в нашей ламповой беседе)'}}

    def checkOnAdmin(self,groupid,userid):
        try:
            data = json.load(open('base.json',encoding='utf-8'))
        except:
            data = []
        group_index = self.getGroupIndex(groupdid=groupid)
        if group_index == -1:
            data.append(self.getTemplate(groupid=groupid))
        else:
            for admin in data[group_index]['ADMINS']:
                if admin == userid:
                    return True
        with open('base.json','w',encoding='utf-8') as file:
            json.dump(data,file,indent=2,ensure_ascii=False)
        return False

    def getUserGroups(self,userid):
        group_list = []
        try:
            data = json.load(open('base.json',encoding='utf-8'))
        except:
            return False
        for group_index in range(len(data)):
            for admin in data[group_index]['ADMINS']:
                if admin == userid:
                    group_list.append(data[group_index]['GROUP_ID'])
        return group_list

    def getUserTemplate(self,userid):
        return {'Nick':self.api.users.get(user_ids=userid)[0]['first_name'],'Money':0,'Exp':0,'Lvl':1}

    def checkAction(self,action,memberid,groupid):
        data = json.load(open('base.json',encoding='utf-8'))
        if action['type'] == 'chat_kick_user':
            if action['member_id'] == memberid:
                if self.getGroupIndex(groupdid=groupid) == -1:
                    return False
                if data[self.getGroupIndex(groupdid=groupid)]['Options']['AutoKick'] == 0:
                    return False
                try:
                    self.api.messages.removeChatUser(chat_id=(groupid)%2000000000,user_id=memberid)
                    self.api.messages.send(message='Система АвтоКика кикнула пользователя vk.com/id{0}.'.format(memberid),peer_id=groupid,random_id=0)
                    if self.checkOnAdmin(groupid=groupid,userid=action['member_id']) == True:
                        with open('base.json','w',encoding='utf-8') as file:
                            data[self.getGroupIndex(groupid)]['ADMINS'].pop(data[self.getGroupIndex(groupid)]['ADMINS'].index(action['member_id']))
                            json.dump(data,file,indent=2,ensure_ascii=False)
                except Exception as Err:
                    if Err == '[27]':
                        self.api.messages.send(message='Чтобы вы могли пользоваться этими функциями дайте мне администратора в беседе.',peer_id=groupid,random_id=0)
                return True
            else:
                if self.checkOnAdmin(userid=action['member_id'],groupid=groupid) == True:
                    data[self.getGroupIndex(groupid)]['ADMINS'].pop(data[self.getGroupIndex(groupid)]['ADMINS'].index(action['member_id']))
                    with open('base.json','w',encoding='utf-8') as file:
                        json.dump(data,file,indent=2,ensure_ascii=False)
                    return True

        if action['type'] == 'chat_invite_user':
            if action['member_id'] != memberid and action['member_id'] != -186270205:
                if self.getGroupIndex(groupdid=groupid) == -1:
                    return False
                self.api.messages.send(message='[id{0}|{1}], {2}'.format(str(action['member_id']),self.api.users.get(user_ids=action['member_id'])[0]['first_name'],data[self.getGroupIndex(groupid)]['Options']['Greeting']),peer_id=groupid, random_id=0)
                return True
            elif action['member_id'] == -186270205:
                self.api.messages.send(message='Всем привет! С вами сегодня Moscow Bot!😱🆒.',peer_id =groupid,random_id=0)
                self.api.messages.send(message='Используйте комманду !меню чтобы ознакомиться с ботом!🆕.',peer_id=groupid,random_id=0)
                self.api.messages.send(message='P.S Рекомендуемо-обязательно дать боту администратора.',peer_id=groupid, random_id=0)
                if self.getGroupIndex(groupid) == -1:
                    data.append(self.getTemplate(groupid))
                    with open('base.json','w',encoding='utf-8') as file:
                        json.dump(data,file,indent=2,ensure_ascii=False)
                    return True

        if action['type'] == 'chat_invite_user_by_link':
            self.api.messages.send(message='[id{0}|{1}],{2}'.format(str(action['member_id']),self.api.users.get(user_ids=action['member_id'])[0]['first_name'],data[self.getGroupIndex(groupid)]['Options']['Greeting']), peer_id=groupid, random_id=0)
            return True

    def checkOnUser(self,groupid,user):
        try:
            data = json.load(open('base.json',encoding='utf-8'))
        except Exception as err:
            print('Error {0}'.format(err))
            return False
        if self.getGroupIndex(groupid) == -1:
            return False
        if data[self.getGroupIndex(groupid)]['Users'].get('User_{0}'.format(user)) == None:
            return False
        return True

    def getChatButtons(self,userid):
        keyboard = VkKeyboard(one_time=True)
        for i in self.getUserGroups(userid=userid):
            keyboard.add_button('!беседа {0}'.format(i),color=VkKeyboardColor.POSITIVE)
        return keyboard.get_keyboard()

    def getUserParametr(self,groupid,user,parametr):
        data = json.load(open('base.json', encoding='utf-8'))
        return data[self.getGroupIndex(groupid)]['Users']['User_{0}'.format(user)].get(parametr)

    def setUserParametr(self,groupid,userid,parametr,value):
        data = json.load(open('base.json', encoding='utf-8'))
        data[self.getGroupIndex(groupid)]['Users'].get('User_{0}'.format(userid))[parametr] = value
        with open('base.json','w',encoding='utf-8') as file:
            json.dump(data,file,indent=2,ensure_ascii=False)
        return True

    def getOwner(self,groupid):
        for i in self.api.messages.getConversationMembers(peer_id=groupid)['items']:
            if i.get('is_owner') == True:
                return i['member_id']
        return False
    def checkMessage(self, message, fromid, peerid):
        if len(message.split()) == 0:
            if peerid != fromid:
                if peerid != fromid:
                    exp = 1
                    self.setUserParametr(peerid, fromid, 'Exp', self.getUserParametr(peerid, fromid, 'Exp') + exp)
                    if self.getUserParametr(peerid, fromid, 'Exp') >= 80*1.45 ** self.getUserParametr(peerid, fromid,'Lvl') - 1:
                        self.setUserParametr(peerid, fromid, 'Lvl', self.getUserParametr(peerid, fromid, 'Lvl') + 1)
                        self.setUserParametr(peerid, fromid, 'Exp', 0)
                        self.api.messages.send(message='[id{id}|{name}],Поздравляю вас с повышением уровня!😃\n Ваш текуший уровень {lvl}🆕'.format(id=fromid, name=self.getUserParametr(peerid, fromid, 'Nick'),lvl=self.getUserParametr(peerid, fromid, 'Lvl')), peer_id=peerid, random_id=0)
            return False
        message = message.split()
        message[0] = message[0].lower()
        message = ' '.join(message)
        if str.find(message.split()[0],'@public186270205') != -1:
            print('Есть упоминание')
            message = message.split(None,1)[1]
        if peerid != fromid:
            if self.getGroupIndex(peerid) == -1:
                data = json.load(open('base.json',encoding='utf-8'))
                data.append(self.getTemplate(peerid))
                with open('base.json','w',encoding='utf-8') as file:
                    json.dump(data,file,indent=2,ensure_ascii=False)
                data[self.getGroupIndex(peerid)]['Users']['User_{0}'.format(fromid)] = self.getUserTemplate(fromid)
                with open('base.json','w',encoding='utf-8') as file:
                    json.dump(data,file,indent=2,ensure_ascii=False)
            elif self.checkOnUser(peerid,fromid) == False:
                data = json.load(open('base.json', encoding='utf-8'))
                data[self.getGroupIndex(peerid)]['Users']['User_{0}'.format(fromid)] = self.getUserTemplate(fromid)
                with open('base.json', 'w', encoding='utf-8') as file:
                    json.dump(data, file, indent=2, ensure_ascii=False)
        if admin_panel.get(fromid) != None:
            if self.getGroupIndex(admin_panel.get(fromid)) == -1:
                admin_panel[fromid] = None

        if message.split()[0][0] != '!':
            if peerid != fromid:
                exp = 0
                for word in message.split():
                    exp = len(word)
                self.setUserParametr(peerid,fromid,'Exp',self.getUserParametr(peerid,fromid,'Exp')+exp)
                if self.getUserParametr(peerid,fromid,'Exp') >= 80*1.45**self.getUserParametr(peerid,fromid,'Lvl')-1:
                    self.setUserParametr(peerid,fromid,'Lvl',self.getUserParametr(peerid,fromid,'Lvl')+1)
                    self.setUserParametr(peerid,fromid,'Exp',0)
                    self.api.messages.send(message='[id{id}|{name}],Поздравляю вас с повышением уровня!😃\n Ваш текуший уровень {lvl}🆕'.format(id=fromid,name=self.getUserParametr(peerid,fromid,'Nick'),lvl=self.getUserParametr(peerid,fromid,'Lvl')),peer_id=peerid,random_id=0)
            return True
        if message.split()[0] == "!привет":
            greetings = ["Привет! Меня ещё создают так что функционал пока что не большой,но вскоре он станет больше"]
            self.api.messages.send(message=random.choice(greetings), peer_id=peerid, random_id=0)
            return True
        if message.split()[0] == "!админ":
            self.api.messages.send(message='Здравствуйте! Вы находитесь у входа в Админ-Панель. Сейчас вас просканирует GEESER...👤', peer_id=peerid, random_id=0)
            if peerid == fromid:
                if self.getUserGroups(userid=fromid) == []:
                    self.api.messages.send(message='Не найдено ни одной беседы где вы администратор.🔇',peer_id=peerid,random_id=0)
                    return False
                self.api.messages.send(message='Добро пожаловать хозяин! Выберите беседу для администрирования.👥',peer_id=fromid, random_id=0)
                groups = self.getUserGroups(userid=fromid)
                self.api.messages.send(message='!беседа ' + '\n!беседа '.join(str(group) for group in groups),keyboard=self.getChatButtons(fromid), peer_id=fromid, random_id=0)
                return True
            if self.checkOnAdmin(groupid=peerid,userid=fromid) == False:
                self.api.messages.send(message='Хмм... Зачем обманывать? Уходи отсюда!😡', peer_id=peerid, random_id=0)
                return False
            else:
                try:
                    self.api.messages.send(message='Добро пожаловать хозяин! Выберите беседу для администрирования.👥',peer_id=fromid,random_id=0)
                except Exception as err:
                    if str(err).split()[0] == '[901]':
                        self.api.messages.send(message='Хозяин,вы запретили мне сообщения 😔... Чтобы разрешить вступите в группу и отправьте любое сообщение.',peer_id=peerid,random_id=0)
                        return False
                groups = self.getUserGroups(userid=fromid)
                chat_keyboard = self.getChatButtons(userid=fromid)
                self.api.messages.send(message='!беседа '+'\n!беседа '.join(str(group) for group in groups),keyboard=chat_keyboard,peer_id=fromid,random_id=0)
                self.api.messages.send(message='ID Беседы - {0}🙏🏻'.format(peerid),peer_id=peerid,random_id=0)
                self.api.messages.send(message='Извините,хозяин,но это очень ценная информация,ожидаю вас в ЛС.🔞', peer_id=peerid, random_id=0)
                return True
        if message.split()[0] == '!беседа':
            if peerid != fromid:
                self.api.messages.send(message='Используйте эту комманду только в ЛС. Информация которую вы сейчас получите очень ценна!⛔',peer_id=peerid,random_id=0)
                return False
            if len(message.split()) == 1:
                groups = self.getUserGroups(userid=fromid)
                chat_keyboard = self.getChatButtons(userid=fromid)
                self.api.messages.send(message='!беседа ' + '\n!беседа '.join(str(group) for group in groups),keyboard=chat_keyboard, peer_id=fromid, random_id=0)
                return False
            if message.split()[1].isdigit() == False:
                groups = self.getUserGroups(userid=fromid)
                chat_keyboard = self.getChatButtons(userid=fromid)
                self.api.messages.send(message='!беседа ' + '\n!беседа '.join(str(group) for group in groups),keyboard=chat_keyboard, peer_id=fromid, random_id=0)
                return False
            if self.checkOnAdmin(groupid=int(message.split()[1]),userid=fromid) == False:
                self.api.messages.send(message='ERROR!!!',peer_id=peerid,random_id=0)
                admin_panel[fromid] = None
                return False
            keyboard = VkKeyboard(one_time=True)
            keyboard.add_button('!Настройки-беседы.👥', color=VkKeyboardColor.POSITIVE)

            keyboard.add_line()

            keyboard.add_button('!Наказания.⛔', color=VkKeyboardColor.NEGATIVE)

            keyboard.add_line()

            keyboard.add_button('!Выдать-Админку.⚠', color=VkKeyboardColor.PRIMARY)
            self.api.messages.send(message='Добро пожаловать хозяин! Что вы желаете сделать в беседе {0}?'.format(message.split()[1]),keyboard=keyboard.get_keyboard(),random_id=0,peer_id=peerid)
            admin_panel[fromid] = int(message.split()[1])
            return True
        if message.split()[0] == '!настройки-беседы.👥' or message.split()[0] == '!настройки-беседы.' or message.split()[0] == '!настройки-беседы':
            if peerid != fromid:
                self.api.messages.send(message='Используйте эту комманду только в ЛС. Информация которую вы сейчас получите очень ценна!⛔',peer_id=peerid,random_id=0)
                return False
            if admin_panel.get(fromid) == None:
                self.api.messages.send(message='Используйте сначало !беседа [ID беседы],или же просто напишите !админ', peer_id=peerid, random_id=0)
                return False
            if self.checkOnAdmin(userid=fromid, groupid=admin_panel.get(fromid)) == False:
                self.api.messages.send(message='ERROR!!!', peer_id=peerid, random_id=0)
                admin_panel[fromid] = None
                return False
            keyboard = VkKeyboard(one_time=True)
            keyboard.add_button('!Вернуться в Админ-Панель', color=VkKeyboardColor.DEFAULT)
            keyboard.add_button('!вернуться к Выбору Бесед', color=VkKeyboardColor.DEFAULT)
            self.api.messages.send(message='Держи список комманд для управления беседы: \n1.!сменить-имя [Новое имя беседы];\n2.!автокик [1 или 0] (Автокик после выхода из беседы);\n3.!приветствие [Приветствие];\n\nP.S На этом пока всё,но скоро будет намного больше возможностей!📢',peer_id=peerid,random_id=0,keyboard=keyboard.get_keyboard())
            return True
        if message.split()[0] == '!сменить-имя':
            if peerid != fromid:
                self.api.messages.send(message='Используйте эту комманду только в ЛС. Информация которую вы сейчас получите очень ценна!⛔',peer_id=peerid,random_id=0)
                return False
            if admin_panel.get(fromid) == None:
                self.api.messages.send(message='Используйте сначало !беседа [ID беседы],или же просто напишите !админ',peer_id=peerid,random_id=0)
                return False
            if self.checkOnAdmin(userid=fromid,groupid=admin_panel.get(fromid)) == False:
                self.api.messages.send(message='ERROR!!!',peer_id=peerid, random_id=0)
                admin_panel[fromid] = None
                return False
            keyboard = VkKeyboard(one_time=True)
            keyboard.add_button('!Вернуться в Админ-Панель', color=VkKeyboardColor.DEFAULT)
            keyboard.add_button('!вернуться к Выбору Бесед', color=VkKeyboardColor.DEFAULT)
            if len(message.split()) == 1:
                self.api.messages.send(message='Используйте !сменить-имя [Новое имя беседы]',peer_id=peerid,random_id=0,keyboard=keyboard.get_keyboard())
                return False
            chatid=(admin_panel[fromid])%200000000
            name = message.split()
            name.pop(0)
            try:
                self.api.messages.editChat(chat_id=chatid,title=' '.join(name))
                self.api.messages.send(message='Имя беседы изменено на - "{0}", Администратором - @id{1}'.format(' '.join(name),fromid),peer_id=admin_panel.get(fromid),random_id=0)
                self.api.messages.send(message='Успешно!✅',peer_id=peerid, random_id=0)
            except Exception as error:
                if error.split()[0] == '[27]':
                    self.api.messages.send('Чтобы вы могли пользоваться этими функциями дайте мне администратора в беседе.')
            keyboard = VkKeyboard(one_time=True)
            keyboard.add_button('!Настройки-беседы.👥', color=VkKeyboardColor.POSITIVE)

            keyboard.add_line()

            keyboard.add_button('!Наказания.⛔', color=VkKeyboardColor.NEGATIVE)

            keyboard.add_line()

            keyboard.add_button('!Выдать-Админку.⚠', color=VkKeyboardColor.PRIMARY)
            self.api.messages.send(message='Добро пожаловать хозяин! Что вы желаете сделать в беседе {0}?'.format(admin_panel.get(fromid)),keyboard=keyboard.get_keyboard(), random_id=0, peer_id=peerid)
            return True
        if message.split()[0] == '!выдать-админку.⚠' or message.split()[0] == '!выдать-админку' or message.split()[0] == '!выдать-админку':
            if peerid != fromid:
                self.api.messages.send(message='Используйте эту комманду только в ЛС. Информация которую вы сейчас получите очень ценна!⛔',peer_id=peerid,random_id=0)
                return False
            if admin_panel.get(fromid) == None:
                self.api.messages.send(message='Используйте сначало !беседа [ID беседы],или же просто напишите !админ',peer_id=peerid, random_id=0)
                return False
            if self.checkOnAdmin(userid=fromid,groupid=admin_panel.get(fromid)) == False:
                self.api.messages.send(message='ERROR!!!', peer_id=peerid, random_id=0)
                admin_panel[fromid] = None
                return False
            keyboard = VkKeyboard(one_time=True)
            keyboard.add_button('!Вернуться в Админ-Панель', color=VkKeyboardColor.DEFAULT)
            keyboard.add_button('!вернуться к Выбору Бесед', color=VkKeyboardColor.DEFAULT)
            if len(message.split()) == 1:
                self.api.messages.send(message='Используйте !выдать-админку [ID пользователя]',peer_id=peerid,random_id=0,keyboard=keyboard.get_keyboard())
                return False
            if message.split()[1].isdigit() == False:
                self.api.messages.send(message='Используйте !выдать-админку [ID пользователя]',peer_id=peerid,random_id=0,keyboard=keyboard.get_keyboard())
                return False
            if self.checkOnAdmin(groupid=admin_panel.get(fromid),userid=int(message.split()[1])) == True:
                self.api.messages.send(message='Этот пользователь уже администратор!🗣',peer_id=peerid,random_id=0,keyboard=keyboard.get_keyboard())
                return False
            try:
                data = json.load(open('base.json',encoding='utf-8'))
            except:
                return False
            data[self.getGroupIndex(groupdid=admin_panel[fromid])]['ADMINS'].append(int(message.split()[1]))
            with open('base.json','w',encoding='utf-8') as file:
                json.dump(data,file,indent=2,ensure_ascii=False)
            self.api.messages.send(message='Администратор - @id{0},выдал админку - @id{1}'.format(fromid,message.split()[1]),random_id=0,peer_id=admin_panel.get(fromid))
            self.api.messages.send(message='Успешно!✅', peer_id=peerid, random_id=0)
            keyboard = VkKeyboard(one_time=True)
            keyboard.add_button('!Настройки-беседы.👥', color=VkKeyboardColor.POSITIVE)

            keyboard.add_line()

            keyboard.add_button('!Наказания.⛔', color=VkKeyboardColor.NEGATIVE)

            keyboard.add_line()

            keyboard.add_button('!Выдать-Админку.⚠', color=VkKeyboardColor.PRIMARY)
            self.api.messages.send(message='Добро пожаловать хозяин! Что вы желаете сделать в беседе {0}?'.format(admin_panel.get(fromid)),keyboard=keyboard.get_keyboard(), random_id=0, peer_id=peerid)
            return True
        if message.split()[0] == '!автокик':
            if peerid != fromid:
                self.api.messages.send(message='Используйте эту комманду только в ЛС. Информация которую вы сейчас получите очень ценна!⛔',peer_id=peerid,random_id=0)
                return False
            if admin_panel.get(fromid) == None:
                self.api.messages.send(message='Используйте сначало !беседа [ID беседы],или же просто напишите !админ',peer_id=peerid, random_id=0)
                return False
            if self.checkOnAdmin(userid=fromid,groupid=admin_panel.get(fromid)) == False:
                self.api.messages.send(message='ERROR!!!', peer_id=peerid, random_id=0)
                admin_panel[fromid] = None
                return False
            keyboard = VkKeyboard(one_time=True)
            keyboard.add_button('!Вернуться в Админ-Панель', color=VkKeyboardColor.DEFAULT)
            keyboard.add_button('!вернуться к Выбору Бесед', color=VkKeyboardColor.DEFAULT)
            if len(message.split()) == 1:
                self.api.messages.send(message='Используйте !автокик [1 или 0]',peer_id=peerid,random_id=0,keyboard=keyboard.get_keyboard())
                return False
            if message.split()[1] == '1' or message.split()[1] == '0':
                try:
                    data = json.load(open('base.json',encoding='utf-8'))
                except:
                    return False
                data[self.getGroupIndex(admin_panel.get(fromid))]['Options']['AutoKick'] = int(message.split()[1])
                with open('base.json','w',encoding='utf-8') as file:
                    json.dump(data,file,indent=2,ensure_ascii=False)
                self.api.messages.send(message='Администратор - @id{0},изменил значение параметра АвтоКик на {1}.😱'.format(fromid,message.split()[1]),peer_id=admin_panel.get(fromid),random_id=0)
                self.api.messages.send(message='Успешно!✅', peer_id=peerid, random_id=0)
                keyboard = VkKeyboard(one_time=True)
                keyboard.add_button('!Настройки-беседы.👥', color=VkKeyboardColor.POSITIVE)

                keyboard.add_line()

                keyboard.add_button('!Наказания.⛔', color=VkKeyboardColor.NEGATIVE)

                keyboard.add_line()

                keyboard.add_button('!Выдать-Админку.⚠', color=VkKeyboardColor.PRIMARY)
                self.api.messages.send(message='Добро пожаловать хозяин! Что вы желаете сделать в беседе {0}?'.format(admin_panel.get(fromid)),keyboard=keyboard.get_keyboard(), random_id=0, peer_id=peerid)
                return True

        if message.split()[0] == '!id':
            if peerid == fromid:
                self.api.messages.send(message='Эта комманда работает только в беседах.',peer_id=peerid,random_id=0)
                return False
            if len(message.split()) == 1:
                self.api.messages.send(message='Используйте !id @пользователь',peer_id=peerid,random_id=0)
                return False
            if str.find(message.split()[1],'id') == -1:
                self.api.messages.send(message='Используйте !id @пользователь',peer_id=peerid,random_id=0)
                return False
            if str.find(message.split()[1],'|') == -1:
                self.api.messages.send(message='Используйте !id @пользователь',peer_id=peerid,random_id=0)
                return False
            id = message.split()[1][str.find(message.split()[1],'id')+2:str.find(message.split()[1],'|')]
            if id == '':
                self.api.messages.send(message='Используйте !id @пользователь', peer_id=peerid, random_id=0)
                return False
            if id.isdigit() == False:
                self.api.messages.send(message='Используйте !id @пользователь', peer_id=peerid, random_id=0)
                return False
            self.api.messages.send(message='ID Пользователя - @id{0}, {1}'.format(id,id),peer_id=peerid,random_id=0)
            return True
        if message.split()[0] == '!объявление':
            pass
        if message.split()[0] == '!приветствие' or message.split()[0] == '!greeting':
            if peerid != fromid:
                self.api.messages.send(message='Используйте эту комманду только в ЛС. Информация которую вы сейчас получите очень ценна!⛔',peer_id=peerid,random_id=0)
                return False
            if admin_panel.get(fromid) == None:
                self.api.messages.send(message='Используйте сначало !беседа [ID беседы],или же просто напишите !админ',peer_id=peerid, random_id=0)
                return False
            if self.checkOnAdmin(userid=fromid,groupid=admin_panel.get(fromid)) == False:
                self.api.messages.send(message='ERROR!!!', peer_id=peerid, random_id=0)
                admin_panel[fromid] = None
                return False
            keyboard = VkKeyboard(one_time=True)
            keyboard.add_button('!Вернуться в Админ-Панель', color=VkKeyboardColor.DEFAULT)
            keyboard.add_button('!вернуться к Выбору Бесед', color=VkKeyboardColor.DEFAULT)
            if len(message.split()) == 1:
                self.api.messages.send(message='Используйте !приветствие [Приветсвие]',peer_id=peerid,random_id=0,keyboard=keyboard.get_keyboard())
                return False
            try:
                data = json.load(open('base.json',encoding='utf-8'))
            except:
                self.api.messages(message='Фатальная ошибка!🆘 Отправьте это создателю бота - vk.com/viiruset6rjet, и будете вознаграждены монетами)',peer_id=peerid,random_id=0,keyboard=keyboard)
                return False
            greeting = message.split()
            greeting.pop(0)
            data[self.getGroupIndex(groupdid=admin_panel.get(fromid))]['Options']['Greeting'] = ' '.join(greeting)
            with open('base.json','w',encoding='utf-8') as file:
                json.dump(data,file,indent=2,ensure_ascii=False)
            self.api.messages.send(message='Приветствие изменено на - "{0}", Администратором - @id{1}'.format(' '.join(greeting),fromid),peer_id=admin_panel.get(fromid), random_id=0)
            self.api.messages.send(message='Успешно!✅', peer_id=peerid, random_id=0)
            keyboard = VkKeyboard(one_time=True)
            keyboard.add_button('!Настройки-беседы.👥', color=VkKeyboardColor.POSITIVE)

            keyboard.add_line()

            keyboard.add_button('!Наказания.⛔', color=VkKeyboardColor.NEGATIVE)

            keyboard.add_line()

            keyboard.add_button('!Выдать-Админку.⚠', color=VkKeyboardColor.PRIMARY)
            self.api.messages.send(message='Добро пожаловать хозяин! Что вы желаете сделать в беседе {0}?'.format(admin_panel.get(fromid)),keyboard=keyboard.get_keyboard(), random_id=0, peer_id=peerid)
            return True
        if message.lower() == '!вернуться в админ-панель.' or message.lower() == '!вернуться в админ-панель':
            if peerid != fromid:
                self.api.messages.send(message='Используйте эту комманду только в ЛС. Информация которую вы сейчас получите очень ценна!⛔',peer_id=peerid, random_id=0)
                return False
            if admin_panel.get(fromid) == None:
                self.api.messages.send(message='В данный момент вы не администрируете какую либо группу.🔇 Чтобы начать администрирование используйте !админ',peer_id=peerid,random_id=0)
                return False
            if self.checkOnAdmin(groupid=admin_panel.get(fromid),userid=fromid) == False:
                self.api.messages.send(message='ERROR!!!',peer_id=peerid, random_id=0)
                admin_panel[fromid] = None
                return False
            keyboard = VkKeyboard(one_time=True)
            keyboard.add_button('!Настройки-беседы.👥', color=VkKeyboardColor.POSITIVE)

            keyboard.add_line()

            keyboard.add_button('!Наказания.⛔', color=VkKeyboardColor.NEGATIVE)

            keyboard.add_line()

            keyboard.add_button('!Выдать-Админку.⚠', color=VkKeyboardColor.PRIMARY)
            self.api.messages.send(message='Добро пожаловать хозяин! Что вы желаете сделать в беседе {0}?'.format(admin_panel.get(fromid)),keyboard=keyboard.get_keyboard(), random_id=0, peer_id=peerid)
            return True
        if message.lower() == '!вернуться к выбору бесед' or message.lower() == '!вернуться к выбору бесед.':
            admin_panel[fromid] = None
            self.api.messages.send(message='Здравствуйте! Вы находитесь у входа в Админ-Панель. Сейчас вас просканирует GEESER...👤',peer_id=peerid, random_id=0)
            if peerid == fromid:
                if self.getUserGroups(userid=fromid) == []:
                    self.api.messages.send(message='Не найдено ни одной беседы где вы администратор.🔇', peer_id=peerid,random_id=0)
                    return False
                self.api.messages.send(message='Добро пожаловать хозяин! Выберите беседу для администрирования.👥',peer_id=fromid, random_id=0)
                groups = self.getUserGroups(userid=fromid)
                self.api.messages.send(message='!беседа ' + '\n!беседа '.join(str(group) for group in groups),keyboard=self.getChatButtons(fromid), peer_id=fromid, random_id=0)
                return True
            self.api.messages.send(message='Используйте эту комманду только в ЛС. Информация которую вы сейчас получите очень ценна!⛔',peer_id=peerid,random_id=0)
            return True
        if message.split()[0] == '!наказания' or message.split()[0] == '!наказания.⛔':
            if peerid != fromid:
                self.api.messages.send(message='Используйте эту комманду только в ЛС. Информация которую вы сейчас получите очень ценна!⛔',peer_id=peerid, random_id=0)
                return False
            if admin_panel.get(fromid) == None:
                self.api.messages.send(message='Используйте сначало !беседа [ID беседы],или же просто напишите !админ',peer_id=peerid, random_id=0)
                return False
            if self.checkOnAdmin(userid=fromid, groupid=admin_panel.get(fromid)) == False:
                self.api.messages.send(message='ERROR!!!', peer_id=peerid, random_id=0)
                admin_panel[fromid] = None
                return False
            keyboard = VkKeyboard(one_time=True)
            keyboard.add_button('!Вернуться в Админ-Панель', color=VkKeyboardColor.DEFAULT)
            keyboard.add_button('!вернуться к Выбору Бесед', color=VkKeyboardColor.DEFAULT)
            self.api.messages.send(message='''Комманды для наказания пользователей⛔:
1.🕛!Кик [ID Пользователя]
2.☠!Бан [ID Пользователя] (Банит пользователя навсегда)
3.😷!Разбан [ID Пользователя] (Разбанивает пользователя)
4.👿!Бан-лист
5.🎭!Мут [ID Пользователя] [время]
6.🔊!Размут [ID Пользователя]''',peer_id=peerid,random_id=0,keyboard=keyboard.get_keyboard())
            return True
        if message.split()[0] == '!кик':
            if peerid != fromid:
                self.api.messages.send(message='Используйте эту комманду только в ЛС. Информация которую вы сейчас получите очень ценна!⛔',peer_id=peerid, random_id=0)
                return False
            if admin_panel.get(fromid) == None:
                self.api.messages.send(message='Используйте сначало !беседа [ID беседы],или же просто напишите !админ',peer_id=peerid, random_id=0)
                return False
            if self.checkOnAdmin(userid=fromid, groupid=admin_panel.get(fromid)) == False:
                self.api.messages.send(message='ERROR!!!', peer_id=peerid, random_id=0)
                admin_panel[fromid] = None
                return False
            keyboard = VkKeyboard(one_time=True)
            keyboard.add_button('!Вернуться в Админ-Панель', color=VkKeyboardColor.DEFAULT)
            keyboard.add_button('!вернуться к Выбору Бесед', color=VkKeyboardColor.DEFAULT)
            if len(message.split()) == 1:
                self.api.messages.send(message='Используйте !Кик [ID Пользователя]',peer_id=peerid,random_id=0,keyboard=keyboard.get_keyboard())
                return False
            if message.split()[1].isdigit() == False:
                self.api.messages.send(message='Используйте !Кик [ID Пользователя]', peer_id=peerid, random_id=0,keyboard=keyboard.get_keyboard())
                return False
            if self.checkOnAdmin(admin_panel.get(fromid),int(message.split()[1])) == True:
                if fromid != self.getOwner(admin_panel.get(fromid)):
                    self.api.messages.send(message='Этот пользоватесь Администратор и его может кикнуть только Создатель беседы.',peer_id=peerid,random_id=0,keyboard=keyboard.get_keyboard())
                    return False
            try:
                self.api.messages.removeChatUser(chat_id=admin_panel.get(fromid)%2000000000,user_id=int(message.split()[1]))
                self.api.messages.send(message='Администратор - @id{id},кикнул пользователя - vk.com/id{pid}'.format(id=fromid,pid=message.split()[1]), peer_id=admin_panel.get(fromid), random_id=0)
                self.api.messages.send(message='Успешно!✅', peer_id=peerid, random_id=0,keyboard=keyboard.get_keyboard())
            except Exception as Err:
                if str(Err).split()[0] == '[15]':
                    self.api.messages.send(message='У меня не достаточно прав,чтобы кикнуть этого пользователя.',peer_id=peerid,random_id=0,keyboard=keyboard.get_keyboard())
                    return False
                if str(Err).split()[0] == '[935]':
                    self.api.messages.send(message='Данного пользователя нет в беседе.',peer_id=peerid, random_id=0, keyboard=keyboard.get_keyboard())
                    return False
            return True
        if message.split()[0] == '!меню':
            if peerid == fromid:
                self.api.messages.send(message='Эта комманда работает только в беседах.\n\nP.S Этот бот был сделан специально для бесед.',peer_id=peerid,random_id=0)
                return False
            self.api.messages.send(message='''[id{id}|{name}],💻Список команд (которые доступны на данный момент)
(Пользователи)
1.🏅 !Lvl
2.🥇 !Top_lvl
                                                
(Для админов)
3.👤 !Админ
4.👥 !Админ-лист (список админов)
5.⚡ !Выдать-Админку '''.format(id=fromid,name=self.getUserParametr(peerid,fromid,'Nick')),peer_id=peerid,random_id=0)

            return True
        if message.split()[0] == '!админы' or message.split()[0] == '!админ-лист':
            if peerid == fromid:
                self.api.messages.send(message='Эта комманда работает только в беседах.',peer_id=peerid,random_id=0)
                return False
            data = json.load(open('base.json',encoding='utf-8'))
            if data[self.getGroupIndex(groupdid=peerid)]['ADMINS'] == []:
                self.api.messages.send(message='Администраторов в данной группе нет...\n⁣‌‌‍‍P.S‌‌‍‍‌‌‍‍‌‌‍‍ КАК ТАК?!😱',peer_id=peerid,random_id=0)
                return False
            admins = []
            for i in data[self.getGroupIndex(peerid)]['ADMINS']:
                admins.append('\n{smile}Администратор {name} - vk.com/id{id}'.format(smile=random.choice(['☢','☣','⚠']),name=self.getUserParametr(peerid,i,'Nick'),id=i))
            self.api.messages.send(message='Администраторы в данной группе: '+''.join(admins) ,peer_id=peerid,random_id=0)
            return True
        if message.split()[0] == '!lvl':
            if peerid == fromid:
                self.api.messages.send(message='Эта комманда работает только в беседах.\n\nP.S Этот бот был сделан специально для бесед.',peer_id=peerid,random_id=0)
                return False
            self.api.messages.send(message='[id{id}|{name}], ваш текущий уровень - {lvl}😎.\nДля повышения уровня осталось - {exp} EXP'.format(id=fromid,name=self.getUserParametr(peerid,fromid,'Nick'),lvl=self.getUserParametr(peerid,fromid,'Lvl'),exp=int((80*1.45**self.getUserParametr(peerid,fromid,'Lvl'))-(self.getUserParametr(peerid,fromid,'Exp')))),peer_id=peerid,random_id=0)
            return True
        if message.split()[0] == '!toplvl':
            if peerid == fromid:
                self.api.messages.send(message='Эта комманда работает только в беседах.\n\nP.S Этот бот был сделан специально для бесед.',peer_id=peerid,random_id=0)
                return False
            data = json.load(open('base.json',encoding='utf-8'))
            userlvls = {}
            for key in data[self.getGroupIndex(peerid)]['Users'].keys():
                userlvls[key] = data[self.getGroupIndex(peerid)]['Users'][key]['Lvl']
            userlvls = sorted(userlvls.items(),key=lambda x: x[1],reverse=True)
            print(userlvls)
            textarr = []
            for i in range(1,len(userlvls)+1):
                if i > 3:
                    break
                textarr.append('\n{number}.{Nick} (vk.com/id{id}) - {Lvl} LVL{smile};'.format(number=i,Lvl=self.getUserParametr(peerid,userlvls[i-1][0].replace('User_',''),'Lvl'),Nick=self.getUserParametr(peerid,userlvls[i-1][0].replace('User_',''),'Nick'),id=userlvls[i-1][0].replace('User_',''),smile=random.choice(['😱','😎','😃'])))
            self.api.messages.send(message='Топ Пользователей этой беседы:'+''.join(textarr),peer_id=peerid,random_id=0)
            return True


    def mainListener(self):
        try:
            for event in self.longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    print(event)
                    if event.object.get('action') != None:
                            self.checkAction(action=event.object['action'],memberid=event.object.from_id,groupid=event.object.peer_id)
                    else:
                        self.checkMessage(message=event.object.text, fromid=event.object.from_id, peerid=event.object.peer_id)
        except requests.exceptions.ReadTimeout:
            print('Тайм-аут')


vk = groupClass("2db78121cb8b152f2affab74d213cb8f2c3e94bc9faed556c5638eaa451adf4b14679932a40660dfdc4f5")
vk.mainListener()