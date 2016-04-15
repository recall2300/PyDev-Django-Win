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
    
def mainPageSearchWork(request):
#    current_page = int(request.GET['current_page'])
    searchStr = request.GET['searchStr']
    pageForView = int(request.GET['pageForView'])

    #print pageForView
    #print 'pageForView : '+str(pageForView)

    # 다음은 테이블에서 subject 항목에 대해 LIKE SQL을 수행한다.
    print '1. searchStr : '+searchStr
    totalCnt = DjangoBoard.objects.filter(subject__contains=searchStr).count()
    print 'pageForView : ' + str(pageForView)
    #print 'totalCnt : '+ str(totalCnt)
    print 'totalCnnnnnT : '+str(totalCnt)

    searchStr = "%"+searchStr+"%"
    pagingHelperIns = pagingHelper();
    totalPageList = pagingHelperIns.getTotalPageList(totalCnt, rowsPerPage)
    
    print 'totalPageList : ' + str(totalPageList)

    # Raw SQL에 like 구문 적용방법.. 이 방법 찾다가 삽질 좀 했다.
    boardList = DjangoBoard.objects.raw('select id, subject, name, created_date, mail, memo,hits from sample_djangoboard where subject like %s order by id desc limit %s, %s', [searchStr,(pageForView-1)*rowsPerPage, rowsPerPage])
    searchStr = searchStr.replace("%","")
    
    return render_to_response('mainPageSearch.html', {'boardList': boardList, 'totalCnt': totalCnt, 'pageForView':pageForView ,'searchStr':searchStr, 'totalPageList':totalPageList} )

def updateMainPageWork(request):
    memo_id = request.GET['memo_id']
    current_page = request.GET['current_page']
    searchStr = request.GET['searchStr']
    boardData = DjangoBoard.objects.get(id=memo_id)
    return render_to_response('updatePage.html', {'memo_id': request.GET['memo_id'],'current_page':request.GET['current_page'],'searchStr': request.GET['searchStr'],'boardData': boardData } )

@csrf_exempt
def updateList(request):
    memo_id = request.POST['memo_id']
    current_page = request.POST['current_page']
    searchStr = request.POST['searchStr']

    # Update DataBase
    DjangoBoard.objects.filter(id=memo_id).update(
                                                  mail= request.POST['mail'],
                                                  subject= request.POST['subject'],
                                                  memo= request.POST['memo']
                                                  )

    # Display Page => POST 요청은 redirection으로 처리하자
    url = '/mainPageWork?current_page=' + str(current_page)
    return HttpResponseRedirect(url)

def deletePage(request):
    memo_id = request.GET['memo_id']
    current_page = request.GET['current_page']

    p = DjangoBoard.objects.get(id=memo_id)
    p.delete()
   
    # 마지막 메모를 삭제하는 경우, 페이지를 하나 줄임.
    totalCnt = DjangoBoard.objects.all().count()
    pagingHelperIns = pagingHelper();

    totalPageList = pagingHelperIns.getTotalPageList( totalCnt, rowsPerPage)
    print 'totalPages', totalPageList

    if( int(current_page) in totalPageList):
        print 'current_page No Change'
        current_page=current_page
    else:
        current_page= int(current_page)-1
        print 'current_page--'

    url = '/mainPageWork?current_page=' + str(current_page)
    return HttpResponseRedirect(url)

@csrf_exempt
def searchPage(request):
    searchStr = request.POST['searchStr']
    print 'searchStr', searchStr

    url = '/mainPageSearchWork?searchStr=' + searchStr +'&pageForView=1'
    return HttpResponseRedirect(url)

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


def xmasmain(request):
    return render_to_response('main.html')