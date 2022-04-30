from django.shortcuts import render
from django.http import HttpResponse
from app import supabase
import os
from django.core.files.storage import FileSystemStorage
import altair as alt
from altair import Chart, X, Y, Axis, Data, DataFormat
import pandas as pd
from django.views.decorators.csrf import csrf_exempt,csrf_protect 


# load a simple dataset as a pandas DataFrame
from vega_datasets import data
cars = data.cars()

Total = 1750000

def index(request):
    return HttpResponse("Hello !!!!")
    
def test(request):
    data = supabase.table('student').select("id,name, college").execute()
    return render(request, 'name.html' , {'data' : data})

def nameClose(request):
    return HttpResponse("")

def nameDelete(request, id):
    supabase.table('student').delete().eq('id', id).execute()
    data = supabase.table('student').select("id,name, college").execute()
    return render(request, 'name.html' , {'data' : data})

@csrf_exempt
def nameUpdate(request):
    if request.method == 'GET':
        supabase.table('student').update({
            'name'    : request.GET['name'],
            'college' : request.GET['college']
        }).eq('id',request.GET['id']).execute()

    data = supabase.table('student').select("id,name, college").execute()
    return render(request, 'name.html' , {'data' : data})

def nameCompute(request):
    if 'inputtele' in request.GET and request.GET['inputtele'] != ' ' and len(request.GET['inputtele']) > 0:
            data = supabase.table('student').select("*").eq('telegram_id', request.GET['inputtele']).execute()
            if len(data.data):
                return HttpResponse("This Telegram ID exists in  DB")
            else:
                return HttpResponse("Hello "+request.GET['inputtele'] +", Welcome !!!")

def nameEdit(request, id):
    data = supabase.table('student').select("id,name, college").eq('id',id).execute()
    data = data.data[0]
    return HttpResponse("<br><br> <div id = 'updateForm'>\
                        <form hx-get='/name-update/'  hx-target='#tabMain' hx-swap='innerhtml'   class='form-container'  > \
                        <label for='Name' style='padding-bottom:15px;padding-right:25px;'><b>Name</b></label> \
                        <input name='name' value='{0}'> <br>\
                        <label for='College' style='padding-bottom:15px;padding-right:13px;'><b>College</b></label> \
                        <input name='college' value='{1}'> <br> \
                        <input type='hidden' name='id' value={2}> \
                        <button class='btn btn-success'  > \
                            Save \
                            </button> </button> </form>\
                            <form hx-get='/name-close/'  hx-target='#updateForm' hx-swap='innerhtml'> \
                            <button class='btn btn-danger'  type='submit'> Cancel  </button> </form> \
                            ".format(data['name'], data['college'], id))

def index(request):
    data = supabase.table('student').select("*, student_status(*)").execute()
    return render(request, 'index.html', {'data': data})

def delete(request, id):
    supabase.table('student_status').delete().eq('student_id', id).execute()
    supabase.table('student').delete().eq('id', id).execute()
    data = supabase.table('student').select("*, student_status(*)").execute()
    return render(request, 'index.html', {'data': data})

def close(request):
    return HttpResponse('')


def edit(request, id):
    data = supabase.table('student').select("*, student_status(*)").eq('id',id).execute()
    data = data.data[0]
    name = data['name']
    amount = 0
    date   = None
    status = ''
    if len(data['student_status']):
        amount = data['student_status'][0]['asset_cost']
        date   = data['student_status'][0]['approval_date']
        status = data['student_status'][0]['status']

    if status == 'Approved':
        status = "checked"
    

    return HttpResponse('<div id="updateForm" > \
                         <form hx-get="/update/"  hx-target="#tabMain" hx-swap="innerhtml"   class="form-container"  > \
                        <h3>{1}</h3><br> \
                        <label for="Amount" style="padding-bottom:15px"><b>Amount</b></label> \
                        <input type="number"  name="amount" value={0} required><br> \
                        <label for="Date" style="padding-right:25px; padding-bottom:15px"><b>Date</b></label> \
                        <input type="date" name="date" value={2} required><br> \
                        <input type="checkbox" id="approve" name="decision" value="Approved" {3}> \
                        <label for="approve">Approve</label><br> <br>\
                        <input type="hidden" name="id" value={4}> \
                        <button  type="submit" class="btn btn-success">Update</button> </form>\
                         <form hx-get="/close/"   hx-target="#updateForm" hx-swap="innerhtml"  class="form-container" id="#closeForm" >\
                        <button type="submit"  class="btn btn-danger" >Close</button> \
                        </form> \
                        </div> \
    ' .format(amount, name, date, status,id))

def viz(request):
    data = supabase.table('student').select("*, student_status(*)").execute()
    amount     = supabase.table('student_status').select("asset_cost").execute()
    spent      = sum([ i['asset_cost'] for i in amount.data])
    assetTotal = Total - spent
    
    result = []
    for i in data.data:
        if 'student_status' in i and len(i['student_status']):
            result.append({
                'studentId' : i['id'],
                'name'      : i['name'],
                'college'   : i['college'],
                'amount'    : i['student_status'][0]['asset_cost'],
                'date'      : i['student_status'][0]['approval_date']
            })

    result.append({
                'studentId' : '-',
                'name'      : '-',
                'college'   : '-',
                'amount'    : 0,
                'date'      : '02-01-2022'
            })
    data = pd.DataFrame(result)
    data['date'] = pd.to_datetime(data['date'])
    data['month'] = data['date'].dt.month.astype('str') + '-' + data['date'].dt.year.astype('str')

    ch1 = Chart(
        data = data.groupby(['month']).agg({'amount':'sum'}).reset_index() , height=300, width=400).mark_line().transform_window(
        sort=[{'field': 'month'}],
        frame=[None, 0],
        cumulative_amt='sum(amount)'
    ).encode(
        x='month:O',
        y='cumulative_amt:Q',
        tooltip = ['amount', 'month']
    ).interactive()

    ch2 = Chart(
        data= data.groupby(['college']).agg({'amount':'sum'}).reset_index(), height=300, width=400).mark_bar().encode(
            x='college',
            y='amount'
    ).interactive()

    df =  pd.DataFrame({'category':['spent','balance', 'budget'], 'value':[spent,Total - spent, Total] })

    ch3 = Chart(
            data= df, height=300, width=400).mark_bar(size = 80).encode(
                x='category',
                y='value',
                color = 'category'
        ).interactive()

    
    chart = ch1 | ch2 | ch3

    return HttpResponse(chart.to_html())


def update(request):
    
    if request.method == 'GET': 
      student_id = request.GET['id']
      asset      = request.GET['amount']
      date       = request.GET['date']
      status     = 'Not Approved'
      if 'decision'  in request.GET:
          status     = request.GET['decision']


      supabase.table('student_status').update({
          
          'asset_cost': asset,
          'approval_date': date,
          'status': status
      }).eq('student_id' ,student_id).execute()

    data = supabase.table('student').select("*, student_status(*)").execute()
    return render(request, 'index.html', {'data': data})





@csrf_exempt
def compute(request):

    amount     = supabase.table('student_status').select("asset_cost").execute()
    spent      = sum([ i['asset_cost'] for i in amount.data])
    assetTotal = Total - spent

    if request.method == 'POST':
        if 'inputStud' in request.POST and request.POST['inputStud'] != ' ' and len(request.POST['inputStud']) > 0:
            data = supabase.table('student').select("*").eq('id', request.POST['inputStud']).execute()
            if len(data.data):
                data = supabase.table('student_status').select("*").eq('student_id', request.POST['inputStud']).execute()
                if len(data.data):
                    return HttpResponse("Student exists and got checked")
                return HttpResponse("Student exists")
            else:
                return HttpResponse("Student not exists")

        if 'inputAsset' in request.POST and request.POST['inputAsset'] != ' ' and len(request.POST['inputAsset']) > 0:
            asset = int(request.POST['inputAsset'])
            return HttpResponse("Total Asset Left:- {0}".format(assetTotal - asset))

        if 'inputtele' in request.POST and request.POST['inputtele'] != ' ' and len(request.POST['inputtele']) > 0:
            data = supabase.table('student').select("*").eq('telegram_id', request.POST['inputtele']).execute()
            if len(data.data):
                return HttpResponse("This Telegram ID exists in  DB")
            else:
                return HttpResponse("Hello "+request.POST['inputtele'])
        
        
        

    return HttpResponse("Total Asset Left:- {0}".format(assetTotal))


@csrf_exempt
def admin(request):
    if request.method == 'POST':
        amount     = supabase.table('student_status').select("asset_cost").execute()
        spent      = sum([ i['asset_cost'] for i in amount.data])
        assetTotal = Total - spent
        if  'inputStud' in request.POST :
            id_    = request.POST['inputStud']
            data = supabase.table('student').select("*").eq('id',id_).execute()

            return render(request, 'admin.html', {'data':data.data[0], 'asset_total': assetTotal, 'flag':'True'})
        
        if request.method == 'POST' and 'student_id' in request.POST :
            
            student_id = request.POST['student_id']
            info       = request.POST['inputInfo']
            asset      = request.POST['inputAsset']
            reason     = request.POST['inputReason']
            date       = request.POST['inputDate']
            if 'decision' in request.POST:
                decision   = request.POST['decision']
            else:
                decision  = 'Not Approved'

            
            res = supabase.table('student_status').insert([{
                'student_id' :student_id,
                'asset_cost': asset,
                'asset_info': info,
                'status_info':  reason,
                'approval_date': date,
                'status': decision
            }]).execute()

            return render(request, 'admin.html',{'message': 'Student {0} is approved.'.format(student_id), 'asset_total': assetTotal, 'flag':'False'} )
    
    return render(request, 'admin.html', {'flag':'False'})

@csrf_exempt
def studentRequest(request):
    if request.method == 'POST':
      
      name       = request.POST['inputName']
      telegramId = request.POST['inputtele']
      rollNumber = request.POST['inputRollNo']
      college    = request.POST['inputCollege']
      address    = request.POST['inputAddress']
      phone      = request.POST['inputPhone']
      email      = request.POST['inputEmail']
      aadhar     = request.POST['aadhar']
      income     = request.POST['income']

      res = supabase.table('student').insert([{
          'name' : name,
          'telegram_id': telegramId,
          'college': college,
          'roll_number': rollNumber,
          'address': address,
          'phone': phone, 
          'email':email,
          'aadhar_url': aadhar,
          'income_certificate_url': income
      }]).execute()

      return render(request, 'student.html', {'message': 'Your data got uploaded'} )



    return render(request, 'student.html' )

def uploadFile(request):
    if request.method == 'POST':
        if 'income' in request.FILES and len(request.FILES) == 1:
            request_file = request.FILES['income']  
            bucket = 'income'
        else: 
            request_file = request.FILES['aadhar']
            bucket = 'aadhar'

        print(request.FILES, bucket)

        fs = FileSystemStorage()
        file = fs.save(request_file.name, request_file)
        fileurl = fs.url(file)

        fileurl = fileurl.replace(' ','').split('/')[1:]
        fileurl = fileurl[0] +'/' +fileurl[1]

        res = supabase.storage().StorageFileAPI(bucket).upload(request_file.name,fileurl )

    return render(request, 'student.html' )

