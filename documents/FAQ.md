<h1 align="center">FAQ</h1>
<p align="center">
<a href="https://github.com/msopentechcn/open-hackathon/blob/master/documents/user_guide.md">Pre</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<a href="https://github.com/msopentechcn/open-hackathon/blob/master/documents/README.md">Back to manual</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<a href="javascript::">Next</a>
</p>
========================

## 工作界面里面如何使用“剪贴板”？
  
  在已经连接到后台系统的情况下，通过组合键“Ctrl + Alt + Shift” 打开左侧控制菜单        
  在“Input Method”里面，点击选择“Text input”                  
  选中后该控制菜单会自动关闭，如果未自动关闭，请通过再组合键"Ctrl+Alt +Shift"来关闭；             

  如图所示：
  ![Imgur](http://i.imgur.com/u2qNGgd.png?1)

  注意：               
      1.每次重新连接到后台系统，需要重新操作一次，打开控制菜单选择“Text input”            
      2.在使用剪切板的时候，连接到的后台系统的操作界面里面只接受“Ctrl + X”，“Ctrl +V” ，“Ctrl + C”快捷键使用方式；            
      3.在输入组合键的时候先按住“Ctrl + Alt” 最后按“Shift”

## 键盘操作没得到响应                        

   这个问题，主要在使用IE11的时候，会出现。在其他的IE如Chrom和Firefox都可以正常运行                    
   解决办法：通过按键‘Tab’来让键盘事件触发              
   一旦发现键盘事件丢失都可以通过“tab”来唤醒                

   另外，当屏幕长时间未操作的时候，当前连接着的session会被连接机制clean掉，这个时候就需要刷新页面来进行重新连接
   重连之后，即可恢复正常操作

## 访问后台系统部署的站点
   在平台当中，已经把后台系统的80端口都已经映射到一个可以公网访问的地址端口                    
   该地址就在操作界面左侧标识endpoint的地方，如下图所示：                 
![Imgur](http://i.imgur.com/PTX0U29.jpg)
   而我们只需要在我们后台系统里面把自定义的web服务部署并监听在80端口，即可通过该endpoint访问；                
   Linux 可自动通过nginx或者apache等等服务来配置和部署站点；                   
   Windows 里面自带的IIS已经按照标准配置完成，仅需要部署web站点                 
