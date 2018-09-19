# 测试用数据格式
## Script
脚本用于整理目标视频文件成固定数据格式，方便测试脚本读取并自动化开启测试流程。
## 目标文件夹结构
文件夹共分三级，一级目录打开后为二级目录，内容是以站点名命名的文件夹组（不含“站”字）。二级目录打开后为第三级目录，存放该站点的室内外视频。室内外视频应当是长度为4小时的各个片段，室内外视频应当成对，并且对齐时间戳。命名格式为 *“室X—XX站—XX：XX—XX：XX.XXX”* 。 如，“室内—十陵站—00：00—04：05.avi”。 在运行数据格式制作脚本前请仔细校验相应的文件夹结构和视频命名，尤其注意时间戳的字符长度（是否少0）。
文件夹结构示意如下表：  

<table><tr><th>1级目录</th><th>2级目录</th><th>3级目录</th></tr><tr><td>test</td><td>十陵</td><td>室内—十陵站—00：00—04：05.avi</td></tr><tr><td> </td><td> </td><td>室外—十陵站—00：00—04：05.avi</td></tr><tr><td> </td><td> </td><td>室内—十陵站—04：05—08：05.avi</td></tr><tr><td> </td><td> </td><td>室外—十陵站—04：05—08：05.avi</td></tr><tr><td> </td><td>万州</td><td>室内—万州站—00：00—04：05.avi</td></tr><tr><td> </td><td> </td><td>室外—万州站—00：00—04：05.avi</td></tr></tr><tr><td> </td><td> </td><td>室内—万州站—04：05—08：05.avi</td></tr></tr><tr><td> </td><td> </td><td>室外—万州站—04：05—08：05.avi</td></tr></table> 

## 数据格式
```
[{                                                                   //一个字典为一个站点，站点在list中相继排放 
    Station:                                                         //站点名称
    Properties:{                                                     //站点详细信息
                    inside:{                                         //室内视频信息
                            in_coord_list:[(xxx,xxx),(xxx,xxx)]      //室内矩形坐标组，一个圆括号为一个矩形
                            file_list:[{                             //文件的list，一个字典代表一个文件
                                        path:                        //文件路径
                                        day_night:                   //白天或黑夜
                                       },  
                                       {  
                                        path:  
                                        day_night:  
                                       }]  
                           }  
                    outside:{
                            out_coord:(xxx,xxx)                      //室外四边形区域的定点，共一处
                            file_list:[{  
                                        path:  
                                        day_night:  
                                       },  
                                       {  
                                        path:  
                                        day_night:  
                                       }]  
                            }  
                }  
}]  
```