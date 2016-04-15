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
    return render_to_response('mainPage2.html')

#def writeForm(request):
    #return 

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
