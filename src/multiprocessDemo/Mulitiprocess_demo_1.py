from multiprocessing import Pool
import time,random,os

def get_page(url):
    print('(进程 %s) 下载页面 %s' %(os.getpid(),url))
    time.sleep(random.randint(1,3))
    return url #用url充当下载后的结果

# 回调函数，处理解析结果
def parse_page(page_content):
    print('<进程 %s> 解析页面: %s' %(os.getpid(),page_content))
    time.sleep(1)
    print('{%s 回调函数处理结果:%s}' %(os.getpid(),page_content))


if __name__ == '__main__':
    urls=[
        'http://maoyan.com/board/1',
        'http://maoyan.com/board/2',
        'http://maoyan.com/board/3',
        'http://maoyan.com/board/4',
        'http://maoyan.com/board/5',
        'http://maoyan.com/board/7',

    ]
    p=Pool()
    res_l=[]

    #异步的方式提交任务,然后把任务的结果交给callback处理
    #注意:会专门开启一个进程来处理callback指定的任务(单独的一个进程,而且只有一个)
    for url in urls:
        res=p.apply_async(get_page,args=(url,),callback=parse_page) #非阻塞方式
        res_l.append(res)

    #异步提交完任务后,主进程先关闭p(必须先关闭),然后再用p.join()等待所有任务结束(包括callback)
    p.close()
    p.join()
    print('{主进程 %s}' %os.getpid())

    #收集结果,发现收集的是get_page的结果
    #所以需要注意了:
    #1. 当我们想要在将get_page的结果传给parse_page处理,那么就不需要i.get(),通过指定callback,就可以将i.get()的结果传给callback执行的任务
    #2. 当我们想要在主进程中处理get_page的结果,那就需要使用i.get()获取后,再进一步处理
    for i in res_l: #本例中,下面这两步是多余的
        callback_res=i.get()
        print(callback_res)
