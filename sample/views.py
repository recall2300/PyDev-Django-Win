# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.utils import timezone
from sample.models import DjangoBoard
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect

# Create your views here.
rowsPerPage = 2

def home(request):
    boardList = DjangoBoard.objects.order_by('-id')[0:2]
    current_page = 1

    totalCnt = DjangoBoard.objects.all().count();

    pagingHelperIns = pagingHelper();
    totalPageList = pagingHelperIns.getTotalPageList(totalCnt, rowsPerPage)

    print 'totalPageList', totalPageList

    return render_to_response('mainPage.html',
        {
            'boardList': boardList,
            'totalCnt': totalCnt,
            'current_page':current_page,
            'totalPageList':totalPageList
        })

def home2(request):
    return render_to_response("mainPage2.html")

def writeForm(request):
    return render_to_response("writeForm.html")

@csrf_exempt
def doWrite(request):
    br = DjangoBoard (subject=request.POST['subject'],
                      name=request.POST['name'],
                      mail=request.POST['email'],
                      memo=request.POST['memo'],
                      created_date=timezone.now(),
                      hits=0
                      )
    br.save()
    url = '/mainPageWork?current_page=1'
    
    return HttpResponseRedirect(url)

def mainPageWork(request):
    current_page = int(request.GET['current_page'])
    totalCnt = DjangoBoard.objects.all().count()
    
    print 'current_page=',current_page
    
    boardList = DjangoBoard.objects.raw('select id, subject, name, created_date, mail, memo,hits from sample_djangoboard order by id desc limit %s, %s', [(current_page-1)*rowsPerPage, rowsPerPage])
    
    print 'boardList=',boardList, 'count()=',totalCnt
    
    pagingHelperIns = pagingHelper();
    totalPageList = pagingHelperIns.getTotalPageList( totalCnt, rowsPerPage)
    
    print 'totalPageList', totalPageList
    
    return render_to_response('mainPage.html', {
                                                        'boardList':boardList,
                                                        'totalCnt':totalCnt,
                                                        'current_page':int(current_page),
                                                        'totalPageList':totalPageList
                                                        })

def readPage(request):
    pk = request.GET['memo_id']
    boardData = DjangoBoard.objects.get(id=pk)

    # 조회수를 늘린다.    
    DjangoBoard.objects.filter(id=pk).update(hits=boardData.hits + 1)
    
    return render_to_response('readPage.html', {'memo_id': request.GET['memo_id'],
                                                'current_page':request.GET['current_page'],
                                                'searchStr': request.GET['searchStr'],
                                                'boardData': boardData })
    



class pagingHelper:
    "paging helper class"
    def getTotalPageList(self, total_cnt, rowsPerPage):
        if ((total_cnt % rowsPerPage) == 0):
            self.total_pages = total_cnt / rowsPerPage
            print 'getTotalPage #1'
        else:
            self.total_pages = (total_cnt / rowsPerPage) + 1;
            print 'getTotalPage #2'

        self.totalPageList = []
        for j in range(self.total_pages):
            self.totalPageList.append(j + 1)

        return self.totalPageList

    def __init__(self):
        self.total_pages = 0
        self.totalPageList = 0
