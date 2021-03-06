# @Time : 2019/9/17 14:11
# @Author : lixiang
# @File : userManage.py
# @Software: PyCharm
from flask import Blueprint, request,jsonify

from MyLogger import Logger
from app.models.log import Last_Online
from app.models.user import User, Resource
from datetime import datetime
from app import db, auth
from flask import g

from app.routes import very_permission
from common.errors import ValidationError
UserManage = Blueprint('usermanage', __name__)


#获取当前登录用户信息
@UserManage.route('/curuserInfo', methods=['GET'])
@auth.login_required
def getCurrentUserInfo():
    if request.method == 'GET':
        api_response = {
            "code": 0,
            "msg": "success"
        }
        try:
            currResource = Resource.query.filter(Resource.perms == "modules:usermanage:info").first()
            if currResource==None:
                api_response["code"] = 401
                api_response["msg"] = "当前操作权限实体不存在"
                return jsonify(api_response), 401
            very = very_permission(currResource.id)
            if very==False:
                api_response["code"] = 401
                api_response["msg"] = "该账户无操作权限"
                return jsonify(api_response), 401
            else:
                data = []
                user = User.query.filter(User.accName == g.user).first()
                if user == None:
                    api_response["code"] = 400
                    api_response["msg"] = "该账户不存在"
                    return jsonify(api_response), 400
                data.append(dict(accName=user.accName, userID=user.userID, accType=user.role_id, userName=user.userName,
                                accAttr=user.accAttr, etpName=user.etpName, userDP=user.userDP, userMail=user.userMail,
                                userPhone=user.userPhone, userTel=user.userTel))
                response = dict(list=data)
                api_response['result'] = response
                return jsonify(api_response)
        except Exception as e:
            Logger('error.log', level='error').logger.error("[获取当前用户信息异常]accName:【%s】%s"  % (g.user, e))
            api_response["code"] =  500
            api_response["msg"] = "服务器未知错误"
            return jsonify(api_response),500


#删除指定用户
@UserManage.route('/delete/<string:accName>', methods=['GET'])
@auth.login_required
def deleteUserInfo(accName):
    if request.method == 'GET':
        api_response = {
            "code": 0,
            "msg": "success"
        }
        try:
            currResource = Resource.query.filter(Resource.perms == "modules:usermanage:delete").first()
            if currResource==None:
                api_response["code"] = 401
                api_response["msg"] = "当前操作权限实体不存在"
                return jsonify(api_response), 401
            very = very_permission(currResource.id)
            if very==False:
                api_response["code"] = 401
                api_response["msg"] = "该账户无操作权限"
                return jsonify(api_response), 401
            else:
                user = User.query.filter(User.accName == accName).first()
                if user == None:
                    api_response["code"] = 400
                    api_response["msg"] = "删除失败，账户不存在"
                    return jsonify(api_response), 400
                db.session.delete(user)
                try:
                    db.session.commit()
                except Exception as ie:
                    Logger('error.log', level='error').logger.error("[事务提交失败]accName:【%s】%s" % (accName, ie))
                    db.session.rollback()
                return jsonify(api_response)
        except Exception as e:
            Logger('error.log', level='error').logger.error("[删除用户异常]accName:【%s】%s" % (accName, e))
            api_response["code"] =  500
            api_response["msg"] = "服务器未知错误"
            return jsonify(api_response),500


#获取指定用户信息
@UserManage.route('/info/<string:accName>', methods=['GET'])
@auth.login_required
def getUserInfo(accName):
    if request.method == 'GET':
        api_response = {
            "code": 0,
            "msg": "success"
        }
        try:
            currResource = Resource.query.filter(Resource.perms == "modules:usermanage:info").first()
            if currResource==None:
                api_response["code"] = 401
                api_response["msg"] = "当前操作权限实体不存在"
                return jsonify(api_response), 401
            very = very_permission(currResource.id)
            if very==False:
                api_response["code"] = 401
                api_response["msg"] = "该账户无操作权限"
                return jsonify(api_response), 401
            else:
                data = []
                user = User.query.filter(User.accName == accName).first()
                if user == None:
                    api_response["code"] = 400
                    api_response["msg"] = "该账户不存在"
                    return jsonify(api_response), 400
                data.append(dict(accName=user.accName, userID=user.userID, accType=user.role_id, userName=user.userName,
                                accAttr=user.accAttr, etpName=user.etpName, userDP=user.userDP, userMail=user.userMail,
                                userPhone=user.userPhone, userTel=user.userTel))
                response = dict(list=data)
                api_response['result'] = response
                return jsonify(api_response)
        except Exception as e:
            Logger('error.log', level='error').logger.error("[获取用户信息异常]accName:【%s】%s" % (accName, e))
            api_response["code"] =  500
            api_response["msg"] = "服务器未知错误"
            return jsonify(api_response),500


#获取用户信息列表
@UserManage.route('/list', methods=['GET'])
@auth.login_required
def getUserList():
    if request.method == 'GET':
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
        accName = request.args.get("accName", "")
        etpCode = request.args.get("etpCode", "")
        etpName = request.args.get("etpName", "")
        accType = request.args.get("accType", "")
        filters = {User.status == 1}
        api_response = {
            "code": 0,
            "msg": "success"
        }
        try:
            currResource = Resource.query.filter(Resource.perms == "modules:usermanage:list").first()
            if currResource==None:
                api_response["code"] = 401
                api_response["msg"] = "当前操作权限实体不存在"
                return jsonify(api_response), 401
            very = very_permission(currResource.id)
            if very == False:
                api_response["code"] = 401
                api_response["msg"] = "该账户无操作权限"
                return jsonify(api_response), 401
            else:
                userList = []
                if accName is not "":
                    filters.add(User.accName.like("%"+accName+"%"))
                if etpCode is not "":
                    filters.add(User.accAttr == etpCode)
                if etpName is not "":
                    filters.add(User.etpName.like("%" + etpName + "%"))
                if accType is not "":
                    filters.add(User.role_id == int(accType))
                userlist = User.query.filter(*filters).limit(limit).offset((page - 1) * limit).all()
                sumList = User.query.filter(*filters).all()
                for user in userlist:
                    last_login = Last_Online.query.filter(Last_Online.accName == user.accName).first()
                    if last_login is None:
                        lastLogintime = None
                    else:
                        lastLogintime = last_login.last_login_time
                    userList.append(dict(accName=user.accName, userName=user.userName, accType=user.role_id,
                                         userDP=user.userDP, etpName=user.etpName, createTime=user.create_date, lastLogintime=lastLogintime))
                result = dict(sumcount=len(sumList), detailcount=len(userlist), list=userList)
                api_response['result'] = result
                return jsonify(api_response)
        except Exception as e:
            Logger('error.log', level='error').logger.error("[获取用户列表异常]accName:【%s】%s" % (accName, e))
            api_response["code"] =  500
            api_response["msg"] = "服务器未知错误"
            return jsonify(api_response),500


#修改用户所属角色
@UserManage.route('/update', methods=['POST'])
@auth.login_required
def editUserPermission():
    if request.method == 'POST':
        api_response = {
            "code": 0,
            "msg": "success"
        }
        try:
            currResource = Resource.query.filter(Resource.perms == "modules:usermanage:update").first()
            if currResource==None:
                api_response["code"] = 401
                api_response["msg"] = "当前操作权限实体不存在"
                return jsonify(api_response), 401
            very = very_permission(currResource.id)
            if very == False:
                api_response["code"] = 401
                api_response["msg"] = "该账户无操作权限"
                return jsonify(api_response), 401
            else:
                request_json = request.get_json()
                if 'accName' not in request_json or request_json['accName'] is "":
                    raise ValidationError("参数不能为空")
                accName = request_json['accName']
                if 'accType' not in request_json or request_json['accType'] is "":
                    raise ValidationError("参数不能为空")
                accType = request_json['accType']
                user = User.query.filter(User.accName == accName).first()
                if user == None:
                    api_response["code"] = 400
                    api_response["msg"] = "所修改账户不存在"
                    return jsonify(api_response), 400
                user.role_id = accType
                try:
                    db.session.commit()
                except Exception as ie:
                    Logger('error.log', level='error').logger.error("[事务提交失败]accName:【%s】%s" % (accName, ie))
                    db.session.rollback()
                return jsonify(api_response)
        except Exception as e:
            Logger('error.log', level='error').logger.error("[修改角色异常]accName:【%s】%s" % (accName, e))
            api_response["code"] =  500
            api_response["msg"] = "服务器未知错误"
            return jsonify(api_response),500


#新增用户
@UserManage.route('/save', methods=['POST'])
@auth.login_required
def createUser():
    if request.method == 'POST':
        api_response = {
            "code": 0,
            "msg": "success"
        }
        try:
            currResource = Resource.query.filter(Resource.perms == "modules:usermanage:save").first()
            if currResource==None:
                api_response["code"] = 401
                api_response["msg"] = "当前操作权限实体不存在"
                return jsonify(api_response), 401
            very = very_permission(currResource.id)
            if very == False:
                api_response["code"] = 401
                api_response["msg"] = "该账户无操作权限"
                return jsonify(api_response), 401
            else:
                request_json = request.get_json()
                if 'accName' not in request_json or request_json['accName'] is "":
                    raise ValidationError("参数不能为空")
                accName = request_json['accName']
                if 'password' not in request_json or request_json['password'] is "":
                    raise ValidationError("参数不能为空")
                password = request_json['password']
                if 'accType' not in request_json or request_json['accType'] is "":
                    raise ValidationError("参数不能为空")
                accType = request_json['accType']
                if 'userID' not in request_json or request_json['userID'] is "":
                    raise ValidationError("参数不能为空")
                userID = request_json['userID']
                if 'userName' not in request_json or request_json['userName'] is "":
                    raise ValidationError("参数不能为空")
                userName = request_json['userName']
                if 'accAttr' not in request_json or request_json['accAttr'] is "":
                    raise ValidationError("参数不能为空")
                accAttr = request_json['accAttr']
                if 'etpName' not in request_json or request_json['etpName'] is "":
                    raise ValidationError("参数不能为空")
                etpName = request_json['etpName']
                if 'userDP' not in request_json or request_json['userDP'] is "":
                    raise ValidationError("参数不能为空")
                userDP = request_json['userDP']
                if 'userMail' not in request_json or request_json['userMail'] is "":
                    raise ValidationError("参数不能为空")
                userMail = request_json['userMail']
                if 'userPhone' not in request_json or request_json['userPhone'] is "":
                    raise ValidationError("参数不能为空")
                userPhone = request_json['userPhone']
                if 'userTel' not in request_json or request_json['userTel'] is "":
                    raise ValidationError("参数不能为空")
                userTel = request_json['userTel']
                status = (request_json['status'] if ('status' in request_json) else 1)
                create_user_id = g.user
                create_date = (request_json['create_date'] if ('create_date' in request_json) else datetime.now())
                remarks = (request_json['remarks'] if ('remarks' in request_json) else "")
                newUser = User(accName, userID, userName, userMail, userPhone, userTel, password, status,
                               accType, accAttr, etpName, userDP, create_date, create_user_id, remarks)
                newUser.hash_pwd(password)
                db.session.add(newUser)
                try:
                    db.session.commit()
                except Exception as ie:
                    Logger('error.log', level='error').logger.error("[事务提交失败]accName:【%s】%s" % (accName, ie))
                    db.session.rollback()
                return jsonify(api_response)
        except Exception as e:
            Logger('error.log', level='error').logger.error("[添加用户异常]accName:【%s】%s" % (accName, e))
            api_response["code"] =  500
            api_response["msg"] = "服务器未知错误"
            return jsonify(api_response),500


#修改用户密码
@UserManage.route('/update/pwd/<string:oldPassword>/<string:password>/<string:reppassword>', methods=['GET'])
@auth.login_required
def editUserPassword(oldPassword,password,reppassword):
    if request.method == 'GET':
        api_response = {
            "code": 0,
            "msg": "success"
        }
        try:
            user = User.query.filter(User.accName == g.user).first()
            if user == None:
                api_response["code"] = 400
                api_response["msg"] = "该账户不存在"
                return jsonify(api_response), 400
            elif user.very_password(oldPassword)==False:
                api_response["code"] = 400
                api_response["msg"] = "原始密码输入有误"
                return jsonify(api_response)
            elif password != reppassword:
                api_response["code"] = 400
                api_response["msg"] = "两次密码不一致"
                return jsonify(api_response)
            else:
                user.hash_pwd(password)
                try:
                    db.session.commit()
                except Exception as ie:
                    Logger('error.log', level='error').logger.error("[事务提交失败]accName:【%s】%s" % (g.user, ie))
                    db.session.rollback()
                return jsonify(api_response)
        except Exception as e:
            Logger('error.log', level='error').logger.error("[修改密码异常]accName:【%s】%s" % (g.user, e))
            api_response["code"] =  500
            api_response["msg"] = "服务器未知错误"
            return jsonify(api_response),500


#修改用户信息
@UserManage.route('/sysUser/update', methods=['POST'])
@auth.login_required
def editUser():
    if request.method == 'POST':
        api_response = {
            "code": 0,
            "msg": "success"
        }
        try:
            currResource = Resource.query.filter(Resource.perms == "modules:usermanage:update").first()
            if currResource==None:
                api_response["code"] = 401
                api_response["msg"] = "当前操作权限实体不存在"
                return jsonify(api_response), 401
            very = very_permission(currResource.id)
            if very == False:
                api_response["code"] = 401
                api_response["msg"] = "该账户无操作权限"
                return jsonify(api_response), 401
            else:
                request_json = request.get_json()
                if 'accName' not in request_json or request_json['accName'] is "":
                    raise ValidationError("参数不能为空")
                accName = request_json['accName']
                # if 'userID' not in request_json or request_json['userID'] is "":
                #     raise ValidationError("参数不能为空")
                # userID = request_json['userID']
                # if 'userName' not in request_json or request_json['userName'] is "":
                #     raise ValidationError("参数不能为空")
                # userName = request_json['userName']
                # if 'accAttr' not in request_json or request_json['accAttr'] is "":
                #     raise ValidationError("参数不能为空")
                # accAttr = request_json['accAttr']
                # if 'etpName' not in request_json or request_json['etpName'] is "":
                #     raise ValidationError("参数不能为空")
                # etpName = request_json['etpName']
                # if 'userDP' not in request_json or request_json['userDP'] is "":
                #     raise ValidationError("参数不能为空")
                # userDP = request_json['userDP']
                if 'userMail' not in request_json or request_json['userMail'] is "":
                    raise ValidationError("参数不能为空")
                userMail = request_json['userMail']
                if 'userPhone' not in request_json or request_json['userPhone'] is "":
                    raise ValidationError("参数不能为空")
                userPhone = request_json['userPhone']
                if 'userTel' not in request_json or request_json['userTel'] is "":
                    raise ValidationError("参数不能为空")
                userTel = request_json['userTel']
                # user = User.query.filter(User.accName == accName,User.userID == userID,User.userName == userName,
                #                          User.accAttr == accAttr,User.etpName == etpName,User.userDP == userDP).first()
                user = User.query.filter(User.accName == accName).first()
                if user == None:
                    api_response["code"] = 400
                    api_response["msg"] = "该账户不存在"
                    return jsonify(api_response), 400
                if ('accType' in request_json):
                    user.role_id = request_json['accType']
                user.userMail = userMail
                user.userPhone = userPhone
                user.userTel = userTel
                if ('password' in request_json):
                    user.hash_pwd(request_json['password'])
                if ('status' in request_json):
                    user.status = request_json['status']
                if ('remarks' in request_json):
                    user.remarks = request_json['remarks']
                try:
                    db.session.commit()
                except Exception as ie:
                    Logger('error.log', level='error').logger.error("[事务提交失败]accName:【%s】%s" % (accName, ie))
                    db.session.rollback()
                return jsonify(api_response)
        except Exception as e:
            Logger('error.log', level='error').logger.error("[修改用户信息异常]accName:【%s】%s" % (accName, e))
            api_response["code"] =  500
            api_response["msg"] = "服务器未知错误"
            return jsonify(api_response),500