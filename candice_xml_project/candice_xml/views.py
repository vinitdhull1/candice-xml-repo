from os.path import basename
from django.conf import settings
from django.http import response
from .models import UploadedInputsInfo
import os, glob
from os import path
from zipfile import ZipFile
from django.contrib import auth, messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import shutil
import datetime
import io
from io import BytesIO
from rest_framework.decorators import api_view
from rest_framework.response import Response
from candice_xml.candice_script import generate_candice_xml
#from candice_script import generate_candice_xml

# Create your views here.

@login_required(login_url='login')
def index(request):
    if request.method == "POST" and request.FILES:
        try:
             shutil.rmtree(r""+settings.MEDIA_ROOT+"candice_xml_output/")
        except Exception as dir_del_err:
            print("Error while trying to clean dir--->", dir_del_err)
        file_name = request.FILES['xml_file'].name
        file = request.FILES['xml_file']
        print("-------------DATA----------------")
        str_text = ''
        for line in file:
            str_text = str_text + line.decode()
        
        xml_file = str_text

        try:
            candice_xml_file,candice_html_report = generate_candice_xml(xml_file)

            print(type(candice_xml_file))
            #print(candice_xml_file)
            print("-----------------------------------------")
            print(type(candice_html_report))
            #print(candice_html_report)

            time_stamp = str(datetime.datetime.now().strftime("%Y-%m-%d--|--%H:%M"))
            time_stamp_for_dir = str(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M"))
            user_info = UploadedInputsInfo(user_names=request.user, file_names=file_name,
                                               output_status='SUCCESS', date=time_stamp)
            user_info.save()

            # Directory
            directory = time_stamp_for_dir
  
            # Parent Directory path
            try:
                if not os.path.exists(r""+settings.MEDIA_ROOT+"candice_xml_output"):
                    root_dir_path = os.path.join(r""+settings.MEDIA_ROOT, "candice_xml_output") 
                    os.mkdir(root_dir_path)
            except Exception as err_root_dir_path:
                print("Error while trying to create root directory-->", err_root_dir_path)

            parent_dir = r""+settings.MEDIA_ROOT+"candice_xml_output/"
  
            # Path
            try:
                path = os.path.join(parent_dir, directory)
                os.mkdir(path)
            except Exception as dir_err:
                print("Error while trying to make directory-->", dir_err)

            #open text file
            xml_file = io.open(r""+settings.MEDIA_ROOT+"candice_xml_output/"+time_stamp_for_dir+"/candice_output.xml", "w", encoding="utf-8")
 
            #write string to file
            xml_file.write(candice_xml_file)
 
            #close file
            xml_file.close()

            #open text file
            html_file = io.open(r""+settings.MEDIA_ROOT+"candice_xml_output/"+time_stamp_for_dir+"/candice_error_report.html", "w", encoding="utf-8")
 
            #write string to file
            html_file.write(candice_html_report)
 
            #close file
            html_file.close()

            messages.success(request, "PROCESS STATUS: SUCCESS")
            context = {
                "link_html": "http://192.168.192.149:8071/media/candice_xml_output/"+time_stamp_for_dir+"/candice_error_report.html",
                "link_xml": "http://192.168.192.149:8071/media/candice_xml_output/"+time_stamp_for_dir+"/candice_output.xml"
            }
            return render(request, 'index.html', context)
        except Exception as ERR:
            time_stamp = str(datetime.datetime.now().strftime("%Y-%m-%d--|--%H:%M"))
            user_info = UploadedInputsInfo(user_names=request.user, file_names=file_name,
                                               output_status='FAILED', date=time_stamp)
            user_info.save()
            messages.error(request, ERR)
            context = {}
            return render(request, 'index.html', context)
    return render(request, 'index.html')


@login_required(login_url='login')
def log_out(request):
    auth.logout(request)
    return render(request, 'login.html')


def log_in(request):
    if request.user.is_authenticated:
        return redirect(index)
    else:
        context = {}
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                # return render(request, 'index.html')
                return redirect(index)
            else:
                messages.error(request, 'please enter correct credentials!')
                return render(request, 'login.html', context)
        else:
            return render(request, 'login.html')


@api_view(['GET','POST'])
def candice_xml(request):
    if request.method == "POST":
        try:
             shutil.rmtree(r""+settings.MEDIA_ROOT+"candice_xml_output/")
        except Exception as dir_del_err:
            print("Error while trying to clean dir--->", dir_del_err)
        data = request.data
        file_name = data['xml_file']
        file = request.FILES['xml_file']
        print("-------------DATA----------------")
        str_text = ''
        for line in file:
            str_text = str_text + line.decode()
        
        xml_file = str_text

        try:
            candice_xml_file,candice_html_report = generate_candice_xml(xml_file)

            print(type(candice_xml_file))
            #print(candice_xml_file)
            print("-----------------------------------------")
            print(type(candice_html_report))
            #print(candice_html_report)

            time_stamp = str(datetime.datetime.now().strftime("%Y-%m-%d--|--%H:%M"))
            time_stamp_for_dir = str(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M"))
            user_info = UploadedInputsInfo(user_names=request.user, file_names=file_name,
                                               output_status='SUCCESS', date=time_stamp)
            user_info.save()

            # Directory
            directory = time_stamp_for_dir
  
            # Parent Directory path
            try:
                if not os.path.exists(r""+settings.MEDIA_ROOT+"candice_xml_output"):
                    root_dir_path = os.path.join(r""+settings.MEDIA_ROOT, "candice_xml_output") 
                    os.mkdir(root_dir_path)
            except Exception as err_root_dir_path:
                print("Error while trying to create root directory-->", err_root_dir_path)

            parent_dir = r""+settings.MEDIA_ROOT+"candice_xml_output/"
  
            # Path
            try:
                path = os.path.join(parent_dir, directory)
                os.mkdir(path)
            except Exception as dir_err:
                print("Error while trying to make directory-->", dir_err)

            #open text file
            xml_file = io.open(r""+settings.MEDIA_ROOT+"candice_xml_output/"+time_stamp_for_dir+"/candice_output.xml", "w", encoding="utf-8")
 
            #write string to file
            xml_file.write(candice_xml_file)
 
            #close file
            xml_file.close()

            #open text file
            html_file = io.open(r""+settings.MEDIA_ROOT+"candice_xml_output/"+time_stamp_for_dir+"/candice_error_report.html", "w", encoding="utf-8")
 
            #write string to file
            html_file.write(candice_html_report)
 
            #close file
            html_file.close()
            

            #messages.success(request, "PROCESS STATUS: SUCCESS")
            context = {
                "link_html": "http://192.168.192.149:8071/media/candice_xml_output/"+time_stamp_for_dir+"/candice_error_report.html",
                "link_xml": "http://192.168.192.149:8071/media/candice_xml_output/"+time_stamp_for_dir+"/candice_output.xml"
            }
            return Response({'output':context})
        except Exception as ERR:
            print("------->", ERR)
            time_stamp = str(datetime.datetime.now().strftime("%Y-%m-%d--|--%H:%M"))
            user_info = UploadedInputsInfo(user_names=request.user, file_names=file_name,
                                               output_status='FAILED', date=time_stamp)
            user_info.save()
            #messages.error(request, ERR)
            context = {}
            return Response({'output':context})
    return redirect(index)


