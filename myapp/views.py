import datetime
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group

# Create your views here.
from myapp.models import Users, Review, Brainemotion, Diary, heartbeat


def loginpage_get(request):
    return render(request,'Admin/loginpage.html')

def loginpage_post(request):
    username=request.POST['username']
    password=request.POST['password']
    a=authenticate(request,username=username,password=password)
    if a is not None:
        login(request,a)
        if a.groups.filter(name='Admin'):
            # messages.success(request,'welc')
            return redirect('/myapp/adminhomepage_get/')
        else:
            messages.error('invalid username or password')
            return  redirect('/myapp/loginpage_get/')
    else:
        messages.warning(request,'no users')
        return redirect('/myapp/loginpage_get/')

def logout_get(request):
    logout(request)
    return redirect('/myapp/loginpage_get/')

@login_required(login_url='/myapp/loginpage_get/')
def adminhomepage_get(request):
    return render(request,'Admin/adminhomepage.html')

@login_required(login_url='/myapp/loginpage_get/')
def viewusers_get(request):
    a=Users.objects.all()
    return render(request, 'Admin/viewusers.html',{'data':a})


#######################3
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Count, Avg, Q
from datetime import datetime, timedelta
from django.utils import timezone
import json
from .models import Users, Brainemotion, Diary, heartbeat
from django.db.models.functions import TruncDate


def admin_view_user_overall_graph(request, id):
    try:
        user = get_object_or_404(Users, id=id)

        context = {
            'user': user,
            'user_id': id,
        }
        return render(request, 'Admin/user_overall_graph.html', context)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def get_user_graph_data(request, id):
    try:
        user = get_object_or_404(Users, id=id)

        # Get date range (last 30 days)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)

        # Get daily brain emotions data
        daily_brain_data = Brainemotion.objects.filter(
            USERS_id=id,
            date__range=[start_date, end_date]
        ).values('date').annotate(
            happy=Count('result', filter=Q(result='happy')),
            sad=Count('result', filter=Q(result='sad')),
            surprise=Count('result', filter=Q(result='surprise')),
            angry=Count('result', filter=Q(result='angry')),
            neutral=Count('result', filter=Q(result='neutral')),
            fear=Count('result', filter=Q(result='fear')),
            total=Count('id')
        ).order_by('date')

        # Calculate daily stress for brain emotions
        for day in daily_brain_data:
            if day['total'] > 0:
                day['happy_percent'] = (day['happy'] / day['total']) * 100
                day['sad_percent'] = (day['sad'] / day['total']) * 100
                day['surprise_percent'] = (day['surprise'] / day['total']) * 100
                day['angry_percent'] = (day['angry'] / day['total']) * 100
                day['neutral_percent'] = (day['neutral'] / day['total']) * 100
                day['fear_percent'] = (day['fear'] / day['total']) * 100

                # Calculate stress (based on negative emotions)
                negative_emotions = day['sad'] + day['angry'] + day['fear']
                day['brain_stress'] = (negative_emotions / day['total']) * 100
            else:
                day['brain_stress'] = 0

        # Get daily diary data
        daily_diary_data = Diary.objects.filter(
            USERS__USER_id=user.id,
            date__range=[start_date, end_date]
        ).values('date').annotate(
            happy=Count('id', filter=Q(text_emotion='happy')),
            neutral=Count('id', filter=Q(text_emotion='neutral')),
            sad=Count('id', filter=Q(text_emotion='sadness')),
            fear=Count('id', filter=Q(text_emotion='fear')),
            surprise=Count('id', filter=Q(text_emotion='surprise')),
            total=Count('id')
        ).order_by('date')

        # Calculate daily stress for diary
        for day in daily_diary_data:
            if day['total'] > 0:
                # Stress from negative emotions in diary
                negative_emotions = day['sad'] + day['fear']
                day['diary_stress'] = (negative_emotions / day['total']) * 100
            else:
                day['diary_stress'] = 0

        # Get heartbeat data
        daily_heartbeat_data = heartbeat.objects.filter(
            USERS_id=id,
            date__range=[start_date, end_date]
        ).values('date').annotate(
            avg_heartbeat=Avg('count')
        ).order_by('date')

        # Calculate heartbeat stress
        for day in daily_heartbeat_data:
            hb = day['avg_heartbeat']
            if hb:
                if hb < 60:
                    day['heartbeat_stress'] = 25
                elif hb < 80:
                    day['heartbeat_stress'] = 50
                elif hb < 100:
                    day['heartbeat_stress'] = 75
                else:
                    day['heartbeat_stress'] = 100
            else:
                day['heartbeat_stress'] = 0

        # Get overall statistics
        total_brain_emotions = Brainemotion.objects.filter(USERS_id=id).count()
        total_diary_entries = Diary.objects.filter(USERS_id=id).count()
        total_heartbeat_records = heartbeat.objects.filter(USERS_id=id).count()

        # Get emotion distribution overall
        emotion_distribution = {
            'happy': Brainemotion.objects.filter(USERS_id=id, result='happy').count(),
            'sad': Brainemotion.objects.filter(USERS_id=id, result='sad').count(),
            'surprise': Brainemotion.objects.filter(USERS_id=id, result='surprise').count(),
            'angry': Brainemotion.objects.filter(USERS_id=id, result='angry').count(),
            'neutral': Brainemotion.objects.filter(USERS_id=id, result='neutral').count(),
            'fear': Brainemotion.objects.filter(USERS_id=id, result='fear').count(),
        }

        # Calculate percentages
        if total_brain_emotions > 0:
            for key in emotion_distribution:
                emotion_distribution[key] = round((emotion_distribution[key] / total_brain_emotions) * 100, 2)

        # Get diary emotion distribution
        diary_distribution = {
            'happy': Diary.objects.filter(USERS_id=id, text_emotion='happy').count(),
            'neutral': Diary.objects.filter(USERS_id=id, text_emotion='neutral').count(),
            'sad': Diary.objects.filter(USERS_id=id, text_emotion='sadness').count(),
            'fear': Diary.objects.filter(USERS_id=id, text_emotion='fear').count(),
            'surprise': Diary.objects.filter(USERS_id=id, text_emotion='surprise').count(),
        }

        if total_diary_entries > 0:
            for key in diary_distribution:
                diary_distribution[key] = round((diary_distribution[key] / total_diary_entries) * 100, 2)

        # Calculate overall stress (average of daily stresses)
        all_dates = set()
        stress_data = {}

        for item in daily_brain_data:
            date_str = item['date'].strftime('%Y-%m-%d')
            all_dates.add(date_str)
            if date_str not in stress_data:
                stress_data[date_str] = {'brain_stress': 0, 'diary_stress': 0, 'heartbeat_stress': 0, 'count': 0}
            stress_data[date_str]['brain_stress'] += item.get('brain_stress', 0)
            stress_data[date_str]['count'] += 1

        for item in daily_diary_data:
            date_str = item['date'].strftime('%Y-%m-%d')
            all_dates.add(date_str)
            if date_str not in stress_data:
                stress_data[date_str] = {'brain_stress': 0, 'diary_stress': 0, 'heartbeat_stress': 0, 'count': 0}
            stress_data[date_str]['diary_stress'] += item.get('diary_stress', 0)
            stress_data[date_str]['count'] += 1

        for item in daily_heartbeat_data:
            date_str = item['date'].strftime('%Y-%m-%d')
            all_dates.add(date_str)
            if date_str not in stress_data:
                stress_data[date_str] = {'brain_stress': 0, 'diary_stress': 0, 'heartbeat_stress': 0, 'count': 0}
            stress_data[date_str]['heartbeat_stress'] += item.get('heartbeat_stress', 0)
            stress_data[date_str]['count'] += 1

        # Calculate average stress per day
        for date_str in stress_data:
            count = stress_data[date_str]['count']
            if count > 0:
                stress_data[date_str]['brain_stress'] = stress_data[date_str]['brain_stress'] / count
                stress_data[date_str]['diary_stress'] = stress_data[date_str]['diary_stress'] / count
                stress_data[date_str]['heartbeat_stress'] = stress_data[date_str]['heartbeat_stress'] / count
                stress_data[date_str]['total_stress'] = (
                    0.4 * stress_data[date_str]['brain_stress'] +
                    0.3 * stress_data[date_str]['diary_stress'] +
                    0.3 * stress_data[date_str]['heartbeat_stress']
                )
            else:
                stress_data[date_str]['total_stress'] = 0

        # Sort dates
        sorted_dates = sorted(all_dates)

        # Prepare data for charts
        chart_data = {
            'dates': sorted_dates,
            'brain_stress': [stress_data[date]['brain_stress'] for date in sorted_dates],
            'diary_stress': [stress_data[date]['diary_stress'] for date in sorted_dates],
            'heartbeat_stress': [stress_data[date]['heartbeat_stress'] for date in sorted_dates],
            'total_stress': [stress_data[date]['total_stress'] for date in sorted_dates],
        }

        # Get activity timeline (last 30 days)
        activity_data = []
        for i in range(30):
            date = end_date - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')

            brain_count = Brainemotion.objects.filter(
                USERS_id=id,
                date=date
            ).count()

            diary_count = Diary.objects.filter(
                USERS_id=id,
                date=date
            ).count()

            heartbeat_count = heartbeat.objects.filter(
                USERS_id=id,
                date=date
            ).count()

            activity_data.append({
                'date': date_str,
                'brain_emotions': brain_count,
                'diary_entries': diary_count,
                'heartbeat_records': heartbeat_count,
                'total_activity': brain_count + diary_count + heartbeat_count
            })

        # Prepare response
        response_data = {
            'user': {
                'id': user.id,
                'name': user.name if hasattr(user, 'name') else f"User {user.id}",
                'email': user.email if hasattr(user, 'email') else "",
                'username': user.user if hasattr(user, 'user') else f"user_{user.id}",
                'joined_date': user.date_joined.strftime('%Y-%m-%d') if hasattr(user, 'date_joined') else "N/A",
            },
            'statistics': {
                'total_brain_emotions': total_brain_emotions,
                'total_diary_entries': total_diary_entries,
                'total_heartbeat_records': total_heartbeat_records,
                'emotion_distribution': emotion_distribution,
                'diary_distribution': diary_distribution,
            },
            'chart_data': chart_data,
            'activity_data': activity_data,
        }

        return JsonResponse(response_data)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=400)



@login_required(login_url='/myapp/loginpage_get/')
def viewreview_get(request):
    a=Review.objects.all()
    return render(request, 'Admin/view_reviews.html', {'data': a})

def changepassword_get(request):
    return render(request, 'Admin/changepassword.html')

def changepassword_post(request):
    curpass=request.POST['currentpassword']
    newpass=request.POST['newpassword']
    confpass=request.POST['confirmpassword']
    data=request.user
    if data.check_password(curpass):
        if newpass==confpass:
            data.set_password(newpass)
            data.save()
            messages.success(request,'Password Send Successfully')
            return redirect("/myapp/loginpage_get/")
        else:
            messages.warning(request,'Failed to Send')
            return render(request,'Admin/changepassword.html')
    else:
        messages.warning(request, 'Failed to send')
        return render(request,'Admin/changepassword.html')


def forgotpass_get(request):
   return render(request,'Admin/forgotpassword.html')

def forgotpass_post(request):
    email=request.POST['email']

    if User.objects.filter(username=email):
        import random
        new_pass = random.randint(00000, 99999)

        user = User.objects.get(username=email)
        print(email)

        # Generate new password
        user.password = make_password(str(new_pass))
        user.save()


        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("projectbrain2025@gmail.com", " gufvxyswpjxupznl")  # App Password
        to = email
        subject = "Test Email"
        body = "Your new password is " + str(new_pass)
        msg = f"Subject: {subject}\n\n{body}"
        server.sendmail("s@gmail.com", to, msg)  # Disconnect from the server
        server.quit()
        return redirect('/myapp/loginpage_get/')
    else:
        return redirect('/myapp/forgotpass_get/')



def userlogin_post(request):
    username=request.POST['Username']
    password = request.POST['Password']

    print(username,password)
    check=authenticate(username=username,password=password)
    print(check)
    if check is not None:
        login(request,check)
        if check.groups.filter(name='Users').exists():
           return JsonResponse({'status':'ok','lid':str(check.id)})
        else:
          return JsonResponse({'status':'no'})
    else:
        return JsonResponse({'status': 'no'})



def usersignup_post(request):
    name = request.POST['name']
    gender = request.POST['gender']
    dob=request.POST['dob']
    email = request.POST['email']
    photo= request.FILES['photo']
    phone = request.POST['phone']
    place= request.POST['place']
    password=request.POST['password']
    confirmpassword=request.POST['confirmpassword']


    if password!=confirmpassword:
        return JsonResponse({"Password does not match"})

    a=User.objects.create_user(username=email,password=password)
    a.groups.add(Group.objects.get(name='Users'))
    a.save()

    fs=FileSystemStorage()
    from datetime import datetime
    date=datetime.now().strftime('%Y%m%d%H%M%S')+'.jpg'
    fs.save(date,photo)
    path=fs.url(date)

    obj=Users()
    obj.name=name
    obj.gender=gender
    obj.dob=dob
    obj.email=email
    obj.photo=path
    obj.phone=phone
    obj.place=place
    obj.USER=a
    obj.save()
    return JsonResponse({'status':'ok'})


def userprofile_post(request):
    lid=request.POST['lid']
    a=Users.objects.get(USER=lid)
    return JsonResponse({"status":'ok',
                         'name':a.name,
                         'gender':a.gender,
                         'dob':a.dob,
                         'email':a.email,
                         'photo':a.photo,
                         'phone':a.phone,
                         'place':a.place
                         })


def usereditprofile_post(request):
    name = request.POST['name']
    gender = request.POST['gender']
    dob = request.POST['dob']
    email = request.POST['email']
    phone = request.POST['phone']
    place = request.POST['place']
    lid = request.POST['lid']
    obj = Users.objects.get(USER=lid)

    if 'photo' in request.FILES:
        photo = request.FILES['photo']
        fs = FileSystemStorage()
        date = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.jpg'
        fs.save(date, photo)
        path = fs.url(date)
        obj.photo = path
        obj.save()

    obj.name = name
    obj.gender = gender
    obj.dob = dob
    obj.email = email
    obj.phone = phone
    obj.place = place
    obj.save()
    return JsonResponse({'status': 'ok'})


def user_sendreview_post(request):
    lid=request.POST['lid']
    review=request.POST['review']
    rating=request.POST['rating']
    obj=Review()
    obj.rating=rating
    obj.review=review
    obj.date=datetime.datetime.now().date()
    obj.USERS=Users.objects.get(USER=lid)
    obj.save()
    return JsonResponse({'status':'ok'})

def user_changepassword_post(request):
    lid=request.POST['lid']
    currentpass=request.POST['current']
    newpass=request.POST['new']
    confpass=request.POST['confirm']
    user=User.objects.get(id=lid)
    if user.check_password(currentpass):
        if newpass==confpass:
            user.set_password(newpass)
            user.save()
            return JsonResponse({'status':'ok'})
        else:
            return JsonResponse({'status':'no'})
    else:
        return JsonResponse({'status': 'no'})



def android_forget_password_post(request):
    email = request.POST.get('email')
    if not email:
        return JsonResponse({'status': 'error', 'message': 'Email is required'})

    try:
        user = User.objects.get(username=email)
        print(email)

        # Generate new password
        new_pass = str(random.randint(1000, 9999))
        user.password = make_password(str(new_pass))
        user.save()

        # Email configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "projectbrain2025@gmail.com"
        app_password = "gufvxyswpjxupznl"

        subject = "Your New Password"
        body = f"Your new password is: {new_pass}"
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(message)
        server.quit()

        return JsonResponse({'status': 'ok', 'message': 'Password sent to your email'})

    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Email not found'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Email send error: {str(e)}'})

from django.core.files.storage import FileSystemStorage
from myapp.pred import predict_from_txt
from myapp.models import Brainemotion, Users

def user_upload_text_post(request):
    textfile = request.FILES['filename']
    lid = request.POST['lid']

    fs = FileSystemStorage()
    from datetime import datetime
    filename = datetime.now().strftime('%Y%m%d%H%M%S') + '.txt'
    saved_path = fs.save(filename, textfile)
    full_path = fs.path(saved_path)

    # 🔮 Prediction
    label, probabilities = predict_from_txt(full_path)



    print(label,"=================")

    print(probabilities,"++++++++++++++++++++++++++++")

    # 💾 Save to DB
    b = Brainemotion()
    b.USERS = Users.objects.get(USER_id=lid)
    b.date = datetime.now().today()
    b.result = label
    b.upload = saved_path
    b.save()

    # 📤 Send response to Android
    return JsonResponse({
        'status': 'ok',
        'predicted_emotion': label,
        'probabilities': probabilities
    })

# def user_upload_text_post(request):
#     textfile=request.FILES['filename']
#     lid = request.POST['lid']
#
#     fs=FileSystemStorage()
#     date=datetime.datetime.now().strftime('%Y%m%d%H%M%S')+'.txt'
#     fs.save(date,textfile)
#     path=fs.url(date)
#
#     from myapp.pred import predict_from_txt
#     ll=predict_from_txt(path)
#
#     b = Brainemotion()
#     b.USERS = Users.objects.get(USER_id = lid)
#     b.date = datetime.datetime.now()
#     b.result = ll
#     b.upload= path
#     b.save()
#
#
#
#
#
#     return JsonResponse({'status':'ok'})

import datetime
import cv2
from fer.fer import FER

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F


model_name = "j-hartmann/emotion-english-distilroberta-base"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

def diarycontents(request):

    if request.method != "POST":
        return JsonResponse({'status': 'failed', 'message': 'Invalid request'})

    try:
    # if 1==1:
        lid = request.POST.get('lid')
        content = request.POST.get('content')
        photo = request.FILES['photo']

        print(lid,"llllllllllllllllll")
        print(content,"llllllllllllllllll")
        print(photo,"llllllllllllllllll")

        # if not photo:
        #     return JsonResponse({'status': 'failed', 'message': 'No image received'})
        from  datetime import datetime
        fs = FileSystemStorage()
        filename = datetime.now().strftime('%Y%m%d%H%M%S') + '.jpg'
        saved_name = fs.save(filename, photo)
        file_path = fs.path(saved_name)

        print("wwwwwwwwwwwwwwwwwwwwwwwwwwwww")

        frame = cv2.imread(file_path)

        if frame is None:
            return JsonResponse({'status': 'failed', 'message': 'Image read error'})

        # Run FER
        detector = FER(mtcnn=True)
        results = detector.detect_emotions(frame)

        print("rrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")

        dominant_emotion = ""

        if results:
            emotions = results[0]["emotions"]
            dominant_emotion = max(emotions, key=emotions.get)


        ## emotion fro text


        inputs = tokenizer(content, return_tensors="pt", truncation=True)
        inputs = {key: val.to(device) for key, val in inputs.items()}

        print("eeeeeeeeeeeeeeeeeeeeeeeee")

        # Disable gradient calculation for inference
        with torch.no_grad():
            outputs = model(**inputs)

        logits = outputs.logits
        probabilities = F.softmax(logits, dim=1)

        predicted_class_id = torch.argmax(probabilities, dim=1).item()
        predicted_emotion = model.config.id2label[predicted_class_id]


        print(predicted_emotion)
        print(probabilities.cpu().numpy()[0])


        print("fffffffffffffffffffffffffffffffffff")
        print("LID:", lid)
        print("Content:", content)
        print("Image:", saved_name)
        print("Face emotion:", dominant_emotion)
        print("Text emotion:", predicted_emotion)


        # Save to database
        diary = Diary()
        diary.date = datetime.now().date()
        diary.time = datetime.now().time()
        diary.content = content
        diary.emotion = dominant_emotion
        diary.text_emotion=predicted_emotion
        diary.image = saved_name
        diary.USERS = Users.objects.get(USER=lid)
        diary.save()

        return JsonResponse({
            'status': 'ok',
            'emotion': dominant_emotion
        })

    except Exception as e:

        print("errrrrr",e)
        return JsonResponse({'status': 'error', 'message': str(e)})


def viewdiarycontent(request):
    lid=request.POST['lid']
    a = Diary.objects.filter(USERS__USER_id=lid)
    l=[]
    for i in a:
        l.append({'id':i.id,
                  'date':i.date,
                  'time':i.time,
                  'emotion':i.emotion,
                  'content':i.content
                  })
    print(l)
    return JsonResponse({'status':'ok','data':l})


def editdiarycontent(request):
    did = request.POST['did']
    content = request.POST['content']
    a = Diary.objects.get(id=did)
    a.date = datetime.datetime.now().date()
    a.time = datetime.datetime.now().time()
    a.content = content
    a.emotion = ''
    a.save()
    return JsonResponse({'status': 'ok'})


def editcontent(request):
    id = request.POST['did']
    a = Diary.objects.get(id=id)
    return JsonResponse({'status':'ok',
                         'id': a.id,
                         'date':a.date,
                         'time':a.time,
                         'content':a.content,
                         'emotion':a.emotion
                         })




def deletediarycontent(request):
    did = request.POST['did']
    Diary.objects.get(id=did).delete()
    return JsonResponse({'status':'ok'})


from django.http import JsonResponse
from .models import Diary

def view_emotiongraph(request):

    lid = request.POST.get('lid')


    print(lid,'bbbbbbbb')

    a = Diary.objects.filter(USERS__USER_id=lid)

    l = []

    for i in a:
        l.append({
            'id': i.id,
            'date': str(i.date),   # convert to string
            'time': str(i.time),
            'emotion': i.emotion,
            'text_emotion': i.text_emotion,
            'content': i.content
        })

    print(l)

    return JsonResponse({'status': 'ok', 'data': l})




#
# def user_emotion_count(request):
#     lid = request.POST.get('lid')
#
#     try:
#
#         totalcnt=Brainemotion.objects.filter(USERS__USER=lid).count()
#
#         # Emotion counts
#         happy = (Brainemotion.objects.filter(USERS__USER=lid, result='happy').count()/ totalcnt)*100
#         sad = (Brainemotion.objects.filter(USERS__USER=lid, result='sad').count()/totalcnt)*100
#         surprise = (Brainemotion.objects.filter(USERS__USER=lid, result='surprise').count()/totalcnt)*100
#         angry = (Brainemotion.objects.filter(USERS__USER=lid, result='angry').count()/totalcnt)*100
#         neutral = (Brainemotion.objects.filter(USERS__USER=lid, result='neutral').count()/totalcnt)*100
#         fear = (Brainemotion.objects.filter(USERS__USER=lid, result='fear').count()/totalcnt)*100
#
#         # Heartbeat average
#         hb_avg = heartbeat.objects.filter(USERS__USER=lid).aggregate(avg=Avg('count'))['avg']
#
#
#         diaryemotiontotal=Diary.objects.filter(USERS__USER_id=lid).count()
#         diaryemotion_happy=Diary.objects.filter(USERS__USER_id=lid,text_emotion="happy").count()/diaryemotiontotal
#         diaryemotion_neutral=Diary.objects.filter(USERS__USER_id=lid,text_emotion="neutral").count()/diaryemotiontotal
#         diaryemotion_sad=Diary.objects.filter(USERS__USER_id=lid,text_emotion="sad").count()/diaryemotiontotal
#         diaryemotion_surprise=Diary.objects.filter(USERS__USER_id=lid,text_emotion="surprise").count()/diaryemotiontotal
#         diaryemotion_fear=Diary.objects.filter(USERS__USER_id=lid,text_emotion="fear").count()/diaryemotiontotal
#
#         # diaryemotion_happy*=100
#         # diaryemotion_neutral*=100
#         # diaryemotion_sad*=100
#         # diaryemotion_surprise*=100
#         # diaryemotion_fear*=100
#
#
#         if hb_avg is None:
#             hb_avg = 0
#
#
#         print(diaryemotion_fear,"====")
#         print(diaryemotion_happy,"=====")
#         print(diaryemotion_neutral,"=====")
#         print(diaryemotion_sad,"====")
#         print(diaryemotion_surprise,"======")
#
#
#         diarytotal= (diaryemotion_happy+diaryemotion_neutral)/(diaryemotion_happy+diaryemotion_neutral+diaryemotion_sad+diaryemotion_fear)
#         eegtotal= (happy+surprise)/ (happy+sad+surprise+angry+neutral+fear)
#         hv=hb_avg
#         if hv<60:
#             hv=25
#         elif hv<40:
#             hv=50
#
#
#
#         totalstress= round((.4* eegtotal)+(.3*diarytotal)+(.3*hv),2)
#
#         k={
#             "status": "ok",
#             "happy": (happy),
#             "sad": str(sad),
#             "surprise": str(surprise),
#             "angry": str(angry),
#             "neutral": str(neutral),
#             "fear": str(fear),
#             "mean": str(round(hb_avg,2)),
#             "diaryemotion_happy": diaryemotion_happy,
#             "diaryemotion_neutral": diaryemotion_neutral,
#             "diaryemotion_sad": diaryemotion_sad,
#             "diaryemotion_fear": diaryemotion_fear,
#             "totalstress": totalstress,
#         }
#
#         print(k,"====")
#
#         return JsonResponse({
#             "status": "ok",
#             "happy": (happy),
#             "sad": str(sad),
#             "surprise": str(surprise),
#             "angry": str(angry),
#             "neutral": str(neutral),
#             "fear": str(fear),
#             "mean": str(round(hb_avg,2)),
#             "diaryemotion_happy": diaryemotion_happy,
#             "diaryemotion_neutral": diaryemotion_neutral,
#             "diaryemotion_sad": diaryemotion_sad,
#             "diaryemotion_fear": diaryemotion_fear,
#             "totalstress": totalstress,
#         })
#
#     except:
#         return JsonResponse({'status':'no','message':'no data found'})
#


# #2nd
# from django.http import JsonResponse
# from django.db.models import Avg
# from datetime import datetime
# import logging
#
# logger = logging.getLogger(__name__)
#
#
# def user_emotion_count_daily(request):
#
#     lid = request.POST.get('lid')
#     date_str = request.POST.get('date')
#
#     print(date_str,"date")
#
#     try:
#         if date_str:
#             from datetime import datetime
#             target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
#
#             print(target_date,"ooooooooo")
#         else:
#             from datetime import datetime
#             target_date = datetime.now().date()
#
#         print(f"Processing daily data for user {lid} on date {target_date}")
#
#         brain_emotions = Brainemotion.objects.filter(
#             USERS__USER=lid,
#             date=target_date
#         )
#
#         total_brain_cnt = brain_emotions.count()
#
#         if total_brain_cnt > 0:
#             happy = (brain_emotions.filter(result='happy').count() / total_brain_cnt) * 100
#             sad = (brain_emotions.filter(result='sad').count() / total_brain_cnt) * 100
#             surprise = (brain_emotions.filter(result='surprise').count() / total_brain_cnt) * 100
#             angry = (brain_emotions.filter(result='angry').count() / total_brain_cnt) * 100
#             neutral = (brain_emotions.filter(result='neutral').count() / total_brain_cnt) * 100
#             fear = (brain_emotions.filter(result='fear').count() / total_brain_cnt) * 100
#         else:
#             happy = sad = surprise = angry = neutral = fear = 0
#             print(f"No brain emotion data for date {target_date}")
#
#
#         hb_query = heartbeat.objects.filter(USERS__USER=lid)
#
#         try:
#             hb_query = hb_query.filter(date=target_date)
#         except:
#             print("Heartbeat model doesn't have date field, using all-time data")
#
#         hb_avg = hb_query.aggregate(avg=Avg('count'))['avg']
#         if hb_avg is None:
#             hb_avg = 0
#
#         # Diary emotions for the specific date
#         diary_query = Diary.objects.filter(USERS__USER_id=lid)
#
#         # Try to filter by date if the field exists
#         try:
#             diary_query = diary_query.filter(date=target_date)
#         except:
#             print("Diary model doesn't have date field, using all-time data")
#
#         diary_total = diary_query.count()
#
#         if diary_total > 0:
#             diary_happy = diary_query.filter(text_emotion="happy",emotion='happy').count() / diary_total
#             diary_neutral = diary_query.filter(text_emotion="neutral",emotion='neutral').count() / diary_total
#             diary_sad = diary_query.filter(text_emotion="sadness",emotion='sad').count() / diary_total
#             diary_surprise = diary_query.filter(text_emotion="surprise",emotion='surprise').count() / diary_total
#             diary_fear = diary_query.filter(text_emotion="fear",emotion='fear').count() / diary_total
#         else:
#             diary_happy = diary_neutral = diary_sad = diary_surprise = diary_fear = 0
#             print(f"No diary data for date {target_date}")
#
#         # Calculate diary total ratio (avoid division by zero)
#         diary_numerator = diary_happy + diary_neutral
#         diary_denominator = diary_happy + diary_neutral + diary_sad + diary_fear
#
#         if diary_denominator > 0:
#             diary_total_ratio = diary_numerator / diary_denominator
#         else:
#             diary_total_ratio = 0
#
#         # Calculate EEG total ratio (avoid division by zero)
#         eeg_numerator = happy + surprise
#         eeg_denominator = happy + sad + surprise + angry + neutral + fear
#
#         if eeg_denominator > 0:
#             eeg_total_ratio = eeg_numerator / eeg_denominator
#         else:
#             eeg_total_ratio = 0
#
#         # Calculate heartbeat stress value
#         # if hb_avg < 60:
#         #     hb_stress = 25
#         # elif hb_avg < 80:
#         #     hb_stress = 50
#         # elif hb_avg < 100:
#         #     hb_stress = 75
#         # else:
#         #     hb_stress = 100
#
#         if hb_avg == 0:
#             hb_stress = 0
#         elif hb_avg < 60:
#             hb_stress = 25
#         elif hb_avg < 80:
#             hb_stress = 50
#         elif hb_avg < 100:
#             hb_stress = 75
#         else:
#             hb_stress = 100
#
#         # Normalize values for stress calculation
#         eeg_normalized = max(0, min(1, eeg_total_ratio))
#         diary_normalized = max(0, min(1, diary_total_ratio))
#         hb_normalized = max(0, min(1, hb_stress / 100))
#
#         # Calculate total stress
#         total_stress = round(
#             (0.4 * eeg_normalized) +
#             (0.3 * diary_normalized) +
#             (0.3 * hb_normalized),
#             2
#         ) * 100  # Convert to percentage
#
#         if total_brain_cnt == 0 and diary_total == 0 and hb_avg == 0:
#             total_stress = 0
#
#
#         # Prepare response data
#         response_data = {
#             "status": "success",
#             "date": target_date.strftime('%Y-%m-%d'),
#             "brain_emotions": {
#                 "happy": round(happy, 2),
#                 "sad": round(sad, 2),
#                 "surprise": round(surprise, 2),
#                 "angry": round(angry, 2),
#                 "neutral": round(neutral, 2),
#                 "fear": round(fear, 2),
#                 "total_count": total_brain_cnt
#             },
#             "heartbeat": {
#                 "average": round(hb_avg, 2),
#                 "stress_level": hb_stress
#             },
#             "diary_emotions": {
#                 "happy": round(diary_happy * 100, 2),
#                 "neutral": round(diary_neutral * 100, 2),
#                 "sad": round(diary_sad * 100, 2),
#                 "fear": round(diary_fear * 100, 2),
#                 "surprise": round(diary_surprise * 100, 2),
#                 "total_count": diary_total
#             },
#             "stress_metrics": {
#                 "eeg_stress_ratio": round(eeg_normalized, 3),
#                 "diary_stress_ratio": round(diary_normalized, 3),
#                 "heartbeat_stress": hb_stress,
#                 "total_stress": total_stress
#             }
#         }
#
#         print(f"Daily data response: {response_data}")
#         return JsonResponse(response_data)
#
#     except Exception as e:
#         logger.error(f"Error in user_emotion_count_daily: {str(e)}", exc_info=True)
#         return JsonResponse({
#             'status': 'error',
#             'message': f'Error processing data: {str(e)}'
#         })
#
#

#
# from django.http import JsonResponse
# from django.db.models import Avg
# from datetime import datetime
# import logging
#
# logger = logging.getLogger(__name__)
#
#
# def user_emotion_count_daily(request):
#     try:
#         lid = request.POST.get('lid')
#         date_str = request.POST.get('date')
#
#         print(f"Received request - lid: {lid}, date: {date_str}")
#
#         # Parse date
#         if date_str:
#             target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
#         else:
#             target_date = datetime.now().date()
#
#         print(f"Processing daily data for user {lid} on date {target_date}")
#
#         # Initialize default values
#         happy = sad = surprise = angry = neutral = fear = 0
#         total_brain_cnt = 0
#         hb_avg = 0
#         diary_happy = diary_neutral = diary_sad = diary_surprise = diary_fear = 0
#         diary_total = 0
#
#         # Get brain emotions data
#         try:
#             brain_emotions = Brainemotion.objects.filter(
#                 USERS__USER=lid,
#                 date=target_date
#             )
#             total_brain_cnt = brain_emotions.count()
#
#             if total_brain_cnt > 0:
#                 happy = (brain_emotions.filter(result='happy').count() / total_brain_cnt) * 100
#                 sad = (brain_emotions.filter(result='sad').count() / total_brain_cnt) * 100
#                 surprise = (brain_emotions.filter(result='surprise').count() / total_brain_cnt) * 100
#                 angry = (brain_emotions.filter(result='angry').count() / total_brain_cnt) * 100
#                 neutral = (brain_emotions.filter(result='neutral').count() / total_brain_cnt) * 100
#                 fear = (brain_emotions.filter(result='fear').count() / total_brain_cnt) * 100
#         except Exception as e:
#             print(f"Error fetching brain emotions: {e}")
#
#         # Get heartbeat data
#         try:
#             hb_query = heartbeat.objects.filter(USERS__USER=lid)
#             if hasattr(heartbeat, 'date'):
#                 hb_query = hb_query.filter(date=target_date)
#
#             hb_avg = hb_query.aggregate(avg=Avg('count'))['avg'] or 0
#         except Exception as e:
#             print(f"Error fetching heartbeat data: {e}")
#
#         # Get diary emotions data
#         try:
#             diary_query = Diary.objects.filter(USERS__USER_id=lid)
#             if hasattr(Diary, 'date'):
#                 diary_query = diary_query.filter(date=target_date)
#
#             diary_total = diary_query.count()
#
#             if diary_total > 0:
#                 diary_happy = (diary_query.filter(text_emotion="happy", emotion='happy').count() / diary_total) * 100
#                 diary_neutral = (diary_query.filter(text_emotion="neutral",
#                                                     emotion='neutral').count() / diary_total) * 100
#                 diary_sad = (diary_query.filter(text_emotion="sadness", emotion='sad').count() / diary_total) * 100
#                 diary_surprise = (diary_query.filter(text_emotion="surprise",
#                                                      emotion='surprise').count() / diary_total) * 100
#                 diary_fear = (diary_query.filter(text_emotion="fear", emotion='fear').count() / diary_total) * 100
#         except Exception as e:
#             print(f"Error fetching diary data: {e}")
#
#         # Calculate stress metrics
#         # Diary total ratio
#         diary_numerator = diary_happy + diary_neutral
#         diary_denominator = diary_happy + diary_neutral + diary_sad + diary_fear
#         diary_total_ratio = (diary_numerator / diary_denominator) if diary_denominator > 0 else 0
#
#         # EEG total ratio
#         eeg_numerator = happy + surprise
#         eeg_denominator = happy + sad + surprise + angry + neutral + fear
#         eeg_total_ratio = (eeg_numerator / eeg_denominator) if eeg_denominator > 0 else 0
#
#         # Heartbeat stress level
#         if hb_avg == 0:
#             hb_stress = 0
#         elif hb_avg < 60:
#             hb_stress = 25
#         elif hb_avg < 80:
#             hb_stress = 50
#         elif hb_avg < 100:
#             hb_stress = 75
#         else:
#             hb_stress = 100
#
#         # Normalize values
#         eeg_normalized = max(0, min(1, eeg_total_ratio))
#         diary_normalized = max(0, min(1, diary_total_ratio))
#         hb_normalized = max(0, min(1, hb_stress / 100))
#
#         # Calculate total stress
#         total_stress = round(
#             (0.4 * eeg_normalized) +
#             (0.3 * diary_normalized) +
#             (0.3 * hb_normalized),
#             2
#         ) * 100
#
#         if total_brain_cnt == 0 and diary_total == 0 and hb_avg == 0:
#             total_stress = 0
#
#         # Prepare response data
#         response_data = {
#             "status": "success",
#             "date": target_date.strftime('%Y-%m-%d'),
#             "brain_emotions": {
#                 "happy": round(happy, 2),
#                 "sad": round(sad, 2),
#                 "surprise": round(surprise, 2),
#                 "angry": round(angry, 2),
#                 "neutral": round(neutral, 2),
#                 "fear": round(fear, 2),
#                 "total_count": total_brain_cnt
#             },
#             "heartbeat": {
#                 "average": round(hb_avg, 2),
#                 "stress_level": hb_stress
#             },
#             "diary_emotions": {
#                 "happy": round(diary_happy, 2),
#                 "neutral": round(diary_neutral, 2),
#                 "sad": round(diary_sad, 2),
#                 "fear": round(diary_fear, 2),
#                 "surprise": round(diary_surprise, 2),
#                 "total_count": diary_total
#             },
#             "stress_metrics": {
#                 "eeg_stress_ratio": round(eeg_normalized, 3),
#                 "diary_stress_ratio": round(diary_normalized, 3),
#                 "heartbeat_stress": hb_stress,
#                 "total_stress": total_stress
#             }
#         }
#
#         print(f"Daily data response prepared successfully")
#         return JsonResponse(response_data)
#
#     except Exception as e:
#         print(f"Error in user_emotion_count_daily: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         return JsonResponse({
#             'status': 'error',
#             'message': f'Error processing data: {str(e)}'
#         })



from django.http import JsonResponse
from django.db.models import Avg
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def user_emotion_count_daily(request):
    try:
        lid = request.POST.get('lid')
        date_str = request.POST.get('date')

        print(f"Received request - lid: {lid}, date: {date_str}")

        # Parse date
        if date_str:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            target_date = datetime.now().date()

        print(f"Processing daily data for user {lid} on date {target_date}")

        # Initialize default values
        happy = sad = surprise = angry = neutral = fear = 0
        total_brain_cnt = 0
        hb_avg = 0
        diary_happy = diary_neutral = diary_sad = diary_surprise = diary_fear = 0
        diary_total = 0

        # Get brain emotions data
        try:
            brain_emotions = Brainemotion.objects.filter(
                USERS__USER=lid,
                date=target_date
            )
            total_brain_cnt = brain_emotions.count()

            if total_brain_cnt > 0:
                happy = (brain_emotions.filter(result='happy').count() / total_brain_cnt) * 100
                sad = (brain_emotions.filter(result='sad').count() / total_brain_cnt) * 100
                surprise = (brain_emotions.filter(result='surprise').count() / total_brain_cnt) * 100
                angry = (brain_emotions.filter(result='angry').count() / total_brain_cnt) * 100
                neutral = (brain_emotions.filter(result='neutral').count() / total_brain_cnt) * 100
                fear = (brain_emotions.filter(result='fear').count() / total_brain_cnt) * 100
        except Exception as e:
            print(f"Error fetching brain emotions: {e}")

        # Get heartbeat data
        try:
            hb_query = heartbeat.objects.filter(USERS__USER=lid)
            if hasattr(heartbeat, 'date'):
                hb_query = hb_query.filter(date=target_date)

            hb_avg = hb_query.aggregate(avg=Avg('count'))['avg'] or 0
        except Exception as e:
            print(f"Error fetching heartbeat data: {e}")

        # Get diary emotions data
        try:
            diary_query = Diary.objects.filter(USERS__USER_id=lid)
            if hasattr(Diary, 'date'):
                diary_query = diary_query.filter(date=target_date)

            diary_total = diary_query.count()

            if diary_total > 0:
                # FIXED: Properly filter both text_emotion and emotion fields
                diary_happy = (diary_query.filter(
                    text_emotion__in=["happy", "joy"],
                    emotion='happy'
                ).count() / diary_total) * 100

                diary_neutral = (diary_query.filter(
                    text_emotion__in=["neutral", "calm"],
                    emotion='neutral'
                ).count() / diary_total) * 100

                diary_sad = (diary_query.filter(
                    text_emotion__in=["sadness", "sad", "grief"],
                    emotion='sad'
                ).count() / diary_total) * 100

                diary_surprise = (diary_query.filter(
                    text_emotion__in=["surprise", "shock"],
                    emotion='surprise'
                ).count() / diary_total) * 100

                diary_fear = (diary_query.filter(
                    text_emotion__in=["fear", "anxiety", "worry"],
                    emotion='fear'
                ).count() / diary_total) * 100
        except Exception as e:
            print(f"Error fetching diary data: {e}")

        # Calculate stress metrics
        # Diary total ratio (positive emotions ratio)
        diary_positive = diary_happy + diary_neutral
        diary_total_emotions = diary_happy + diary_neutral + diary_sad + diary_fear + diary_surprise

        if diary_total_emotions > 0:
            diary_total_ratio = diary_positive / diary_total_emotions
        else:
            diary_total_ratio = 0

        # EEG total ratio (positive emotions ratio)
        eeg_positive = happy + surprise
        eeg_total_emotions = happy + sad + surprise + angry + neutral + fear

        if eeg_total_emotions > 0:
            eeg_total_ratio = eeg_positive / eeg_total_emotions
        else:
            eeg_total_ratio = 0

        # Heartbeat stress level
        if hb_avg == 0:
            hb_stress = 0
        elif hb_avg < 60:
            hb_stress = 25  # Low stress
        elif hb_avg < 80:
            hb_stress = 50  # Medium stress
        elif hb_avg < 100:
            hb_stress = 75  # High stress
        else:
            hb_stress = 100  # Very high stress

        # Normalize values (lower eeg_total_ratio and diary_total_ratio = higher stress)
        # So we use (1 - ratio) for stress calculation
        eeg_stress_factor = 1 - eeg_total_ratio
        diary_stress_factor = 1 - diary_total_ratio
        hb_stress_factor = hb_stress / 100

        # Calculate total stress (weighted average)
        total_stress = round(
            (0.4 * eeg_stress_factor * 100) +
            (0.3 * diary_stress_factor * 100) +
            (0.3 * hb_stress_factor * 100),
            2
        )

        # Ensure stress is between 0 and 100
        total_stress = max(0, min(100, total_stress))

        if total_brain_cnt == 0 and diary_total == 0 and hb_avg == 0:
            total_stress = 0

        # Prepare response data
        response_data = {
            "status": "success",
            "date": target_date.strftime('%Y-%m-%d'),
            "brain_emotions": {
                "happy": round(happy, 2),
                "sad": round(sad, 2),
                "surprise": round(surprise, 2),
                "angry": round(angry, 2),
                "neutral": round(neutral, 2),
                "fear": round(fear, 2),
                "total_count": total_brain_cnt
            },
            "heartbeat": {
                "average": round(hb_avg, 2),
                "stress_level": hb_stress
            },
            "diary_emotions": {
                "happy": round(diary_happy, 2),
                "neutral": round(diary_neutral, 2),
                "sad": round(diary_sad, 2),
                "fear": round(diary_fear, 2),
                "surprise": round(diary_surprise, 2),
                "total_count": diary_total
            },
            "stress_metrics": {
                "eeg_stress_ratio": round(eeg_total_ratio, 3),
                "diary_stress_ratio": round(diary_total_ratio, 3),
                "heartbeat_stress": hb_stress,
                "total_stress": total_stress
            }
        }

        print(f"Daily data response: {response_data}")
        return JsonResponse(response_data)

    except Exception as e:
        print(f"Error in user_emotion_count_daily: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'status': 'error',
            'message': f'Error processing data: {str(e)}'
        })


def user_emotion_count(request):
    try:
        lid = request.POST.get('lid')

        # Get total brain emotion count
        totalcnt = Brainemotion.objects.filter(USERS__USER=lid).count()

        if totalcnt == 0:
            return JsonResponse({
                "status": "ok",
                "happy": 0,
                "sad": 0,
                "surprise": 0,
                "angry": 0,
                "neutral": 0,
                "fear": 0,
                "mean": 0,
                "diaryemotion_happy": 0,
                "diaryemotion_neutral": 0,
                "diaryemotion_sad": 0,
                "diaryemotion_fear": 0,
                "totalstress": 0,
            })

        # Emotion counts (as percentages)
        happy = (Brainemotion.objects.filter(USERS__USER=lid, result='happy').count() / totalcnt) * 100
        sad = (Brainemotion.objects.filter(USERS__USER=lid, result='sad').count() / totalcnt) * 100
        surprise = (Brainemotion.objects.filter(USERS__USER=lid, result='surprise').count() / totalcnt) * 100
        angry = (Brainemotion.objects.filter(USERS__USER=lid, result='angry').count() / totalcnt) * 100
        neutral = (Brainemotion.objects.filter(USERS__USER=lid, result='neutral').count() / totalcnt) * 100
        fear = (Brainemotion.objects.filter(USERS__USER=lid, result='fear').count() / totalcnt) * 100

        # Heartbeat average
        hb_avg = heartbeat.objects.filter(USERS__USER=lid).aggregate(avg=Avg('count'))['avg']
        if hb_avg is None:
            hb_avg = 0

        # Diary emotions (as decimals 0-1)
        diaryemotiontotal = Diary.objects.filter(USERS__USER_id=lid).count()

        if diaryemotiontotal > 0:
            diaryemotion_happy = Diary.objects.filter(USERS__USER_id=lid, text_emotion__in=["happy", "joy"],
                                                      emotion='happy').count() / diaryemotiontotal
            diaryemotion_neutral = Diary.objects.filter(USERS__USER_id=lid, text_emotion__in=["neutral", "calm"],
                                                        emotion='neutral').count() / diaryemotiontotal
            diaryemotion_sad = Diary.objects.filter(USERS__USER_id=lid, text_emotion__in=["sadness", "sad", "grief"],
                                                    emotion='sad').count() / diaryemotiontotal
            diaryemotion_surprise = Diary.objects.filter(USERS__USER_id=lid, text_emotion__in=["surprise", "shock"],
                                                         emotion='surprise').count() / diaryemotiontotal
            diaryemotion_fear = Diary.objects.filter(USERS__USER_id=lid, text_emotion__in=["fear", "anxiety", "worry"],
                                                     emotion='fear').count() / diaryemotiontotal
        else:
            diaryemotion_happy = diaryemotion_neutral = diaryemotion_sad = diaryemotion_surprise = diaryemotion_fear = 0

        # Calculate stress metrics
        # Positive emotions ratio for diary
        diary_positive = diaryemotion_happy + diaryemotion_neutral
        diary_total = diaryemotion_happy + diaryemotion_neutral + diaryemotion_sad + diaryemotion_fear + diaryemotion_surprise

        if diary_total > 0:
            diary_ratio = diary_positive / diary_total
        else:
            diary_ratio = 0

        # Positive emotions ratio for EEG
        eeg_positive = (happy + surprise) / 100
        eeg_total = (happy + sad + surprise + angry + neutral + fear) / 100

        if eeg_total > 0:
            eeg_ratio = eeg_positive / eeg_total
        else:
            eeg_ratio = 0

        # Heartbeat stress factor
        if hb_avg == 0:
            hb_stress_factor = 0
        elif hb_avg < 60:
            hb_stress_factor = 0.25
        elif hb_avg < 80:
            hb_stress_factor = 0.5
        elif hb_avg < 100:
            hb_stress_factor = 0.75
        else:
            hb_stress_factor = 1

        # Calculate total stress (using inverse of positive ratios)
        eeg_stress = 1 - eeg_ratio
        diary_stress = 1 - diary_ratio

        totalstress = round(
            (0.4 * eeg_stress * 100) +
            (0.3 * diary_stress * 100) +
            (0.3 * hb_stress_factor * 100),
            2
        )

        # Ensure stress is between 0 and 100
        totalstress = max(0, min(100, totalstress))

        response_data = {
            "status": "ok",
            "happy": happy,
            "sad": sad,
            "surprise": surprise,
            "angry": angry,
            "neutral": neutral,
            "fear": fear,
            "mean": round(hb_avg, 2),
            "diaryemotion_happy": diaryemotion_happy,
            "diaryemotion_neutral": diaryemotion_neutral,
            "diaryemotion_sad": diaryemotion_sad,
            "diaryemotion_fear": diaryemotion_fear,
            "totalstress": totalstress,
        }

        print(f"Overall data response: {response_data}")
        return JsonResponse(response_data)

    except Exception as e:
        print(f"Error in user_emotion_count: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'status': 'error',
            'message': f'Error processing data: {str(e)}'
        })