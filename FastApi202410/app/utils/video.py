from datetime import datetime
import os
import integv
import ffmpeg
import subprocess
from PIL import Image
import cv2
import ffmpeg
from app.core.config import settings
from app.crud import video as video_crud
import time

GIF_FRAMES_MAX = int(settings.GIF_FRAMES_MAX)
GIF_FRAMES_MIN = int(settings.GIF_FRAMES_MIN)
GIF_SIZE = settings.GIF_SIZE
TEMP_DIR = settings.TEMP_DIR
VIDEO_DIR = settings.VIDEO_DIR
WASTE_DIR = settings.WASTE_DIR

class Dbid:
    def __init__(self, dbid):
        VIDEO_DIR = settings.VIDEO_DIR
        GIF_FRAMES_MIN = settings.GIF_FRAMES_MIN
        GIF_FRAMES_MAX  = settings.GIF_FRAMES_MAX
        GIF_SIZE = settings.GIF_SIZE
        self.dbid = dbid
        self.file = VIDEO_DIR + '/' + self.dbid
        self.name = dbid[dbid.rfind('/')+1:dbid.rfind('.')]
        self.dir = dbid[:dbid.rfind('/')]
        self.type = dbid[dbid.rfind('.')+1:]
        self.gifdir = VIDEO_DIR + '/' + self.dir + '/' + 'gif'
        self.webp = VIDEO_DIR + '/' + self.dir + '/' + 'webp/' + self.name + '.webp'
        self.webpdir = VIDEO_DIR + '/' + self.dir + '/' + 'webp'
        self.gif = VIDEO_DIR + '/' + self.dir + '/' + 'gif/' + self.name + '.gif'
        # self.showtime = None
        pass
    def gif_frames(self):
        if GIF_FRAMES_MIN > int(self.showtime / 120):
            return GIF_FRAMES_MIN
        if GIF_FRAMES_MAX < int(self.showtime / 120):
            return GIF_FRAMES_MAX
        else:
            return int(self.showtime / 120)
    def get_gif_cuts(self):
        cut_times = []
        frames = self.gif_frames()
        for i in range(frames):
            cut_times.append(int( ((self.showtime) - i*self.showtime/frames) - self.showtime/(2*frames) ))
        cut_times.sort()
        return cut_times

def createDirectory(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except:
        return False

    
def scan_hddvideofile():
    # print(VIDEO_DIR)
    folders = [i for i in os.listdir(VIDEO_DIR)]
    # print(folders)
    folders.remove('_waste')
    scann_files = []
    for i in folders:
        # print(i)
        _folder = VIDEO_DIR + '/' + i + '/'
        _file = os.listdir(_folder)
        for j in os.listdir(_folder):
            if j not in ['gif', 'webp', '@eaDir', 'Thumbs.db']:
                scann_files.append(_folder + j)
    return scann_files

def scan_gif(_db_gifdir):
    # createDirectory(_db_gifdir)
    gif_scanned_files = []
    for _dir in _db_gifdir:
        try:
            for d in os.listdir(_dir):
                if 'gif' == d[d.rfind('.')+1:]:
                    gif_scanned_files.append(_dir + '/' + d)
        except FileNotFoundError:
            pass
    return gif_scanned_files

def scan_webp(_db_webpdir):
    # createDirectory(_db_webpdir)
    webp_scanned_files = []
    for _dir in _db_webpdir:
        try:
            for d in os.listdir(_dir):
                if 'webp' == d[d.rfind('.')+1:]:
                    webp_scanned_files.append(_dir + '/' + d)
        except FileNotFoundError:
            pass
    return webp_scanned_files

                
    
def check_corruptd_video(_file, file_type):
    print('integv_type: ', file_type)
    try:
        return integv.verify(_file, file_type)
    except OverflowError as e:
        return 'OverflowError'
    except NotImplementedError as e:
        return 'NotImplementedError'
    except FileNotFoundError as e:
        return 'FileNotFoundError'


def get_createDate_ffmpeg(src):
    try:
        vmeta = ffmpeg.probe(src)
        dest = WASTE_DIR + '/' + src[src.rfind('/')+1:]
    except:
        dest = WASTE_DIR + '/' + src[src.rfind('/')+1:]
        # shutil.move(src, dest)
        return "not video file"
    duration = vmeta['format']['duration']
    try:
        date = vmeta['format']['tags']['creation_time']
        date = date[:date.rfind('.')].replace('T', ' ')
        date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    except:
        return ({
            'showtime': int(round(float(duration),0)),
            'cdate': None
        })
    
    return ({
        'showtime': int(round(float(duration),0)),
        'cdate': date,
    })


def cnv_tsTomp4(dbid):
    file = dbid.file
    _ts = file
    _mp4 = file[:file.rfind('.')] + '.mp4'
    command = f'ffmpeg -i {_ts} -acodec copy -vcodec copy {_mp4}'
    subprocess.run(['ffmpeg', '-y', '-i',  _ts, '-acodec', 'copy', '-vcodec', 'copy', _mp4])
    os.remove(_ts)
    return dbid.dbid.replace('ts', 'mp4').replace('TS', 'mp4')

def get_vmeta_ffmpeg(src):
    # print(src)
    try:
        vmeta = ffmpeg.probe(src)
    except ffmpeg._run.Error:
        dest = WASTE_DIR + '/' + src[src.rfind('/')+1:]
        return "not video file"
    bitrate = vmeta['format']['bit_rate']
    duration = vmeta['format']['duration']
    filesize = vmeta['format']['size']
    try:
        width = vmeta['streams'][0]['coded_width']
        height = vmeta['streams'][0]['coded_height']
    except:
        width = vmeta['streams'][1]['coded_width']
        height = vmeta['streams'][1]['coded_height']
    try:
        date = vmeta['format']['tags']['creation_time']
        date = date[:date.rfind('.')].replace('T', ' ')
        date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    except:
        return ({
            'width': int(width),
            'height': int(height),
            'showtime': int(round(float(duration),0)),
            'bitrate': int(bitrate),
            'filesize': int(filesize),
            })
    
    return ({
            'width': int(width),
            'height': int(height),
            'showtime': int(round(float(duration),0)),
            'bitrate': int(bitrate),
            'filesize': int(filesize),
            'cdate': date,
            })

def make_gif(dbid):
    vidcap = cv2.VideoCapture(dbid.file)
    imgs = []
    cut_times = dbid.get_gif_cuts()
    for i, cut_time in enumerate(dbid.get_gif_cuts()):
        fps = vidcap.get(cv2.CAP_PROP_FPS)
        if fps == 1:
            return 'Image file'
        vidcap.set(cv2.CAP_PROP_POS_MSEC, cut_time*1000)
        success, image = vidcap.read()
        if success == False:
            return False
        if success:
            if image.shape[1] > GIF_SIZE:
                image = cv2.resize(image, (GIF_SIZE, int(GIF_SIZE*image.shape[0]/image.shape[1])))
            filename = TEMP_DIR + '/' + str(i).zfill(2) + '.png'
            cv2.imwrite(filename, image)
            imgs.append(filename)
    vidcap.release()
    imgs = [Image.open(f) for f in imgs]
    frame_one = imgs[0]
    frame_one.save(dbid.gif, format='GIF', append_images=imgs,
                   save_all=True, duration=500, loop=0)
    return dbid.gif

def make_webp(dbid):
    vidcap = cv2.VideoCapture(dbid.file)
    vidcap.set(cv2.CAP_PROP_POS_MSEC, dbid.showtime*1000/2)
    success, image = vidcap.read()
    if success == False:
        return False
    if success:
        if image.shape[1] > GIF_SIZE:
            image = cv2.resize(image, (GIF_SIZE, int(GIF_SIZE*image.shape[0]/image.shape[1])))
        cv2.imwrite(dbid.webp, image)
        vidcap.release()
        return dbid.webp

def make_rotate_webp(dbid):
    vidcap = cv2.VideoCapture(dbid.file)
    vidcap.set(cv2.CAP_PROP_POS_MSEC, dbid.showtime*1000/2)
    success, image = vidcap.read()
    if success == False:
        return False
    if success:
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        if image.shape[1] > GIF_SIZE:
            image = cv2.resize(image, (GIF_SIZE, int(GIF_SIZE*image.shape[0]/image.shape[1])))
        cv2.imwrite(dbid.webp, image)
        vidcap.release()
        return dbid.webp

def make_rotate_gif(dbid):
    vidcap =cv2.VideoCapture(dbid.file)
    imgs = []
    for i, cut_time in enumerate(dbid.get_gif_cuts()):
        fps = vidcap.get(cv2.CAP_PROP_FPS)
        if fps == 1:
            return 'Image file'
        vidcap.set(cv2.CAP_PROP_POS_MSEC, cut_time*1000)
        success, image = vidcap.read()
        if success == False:
            return False
        if success:
            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
            if image.shape[1] > GIF_SIZE:
                image = cv2.resize(image, (GIF_SIZE, int(GIF_SIZE*image.shape[0]/image.shape[1])))
            filename = TEMP_DIR + '/' + str(i).zfill(2) + '.png'
            cv2.imwrite(filename, image)
            imgs.append(filename)
    vidcap.release()
    imgs = [Image.open(f) for f in imgs]
    frame_one = imgs[0]
    frame_one.save(dbid.gif, format='GIF', append_images=imgs,
                   save_all=True, duration=500, loop=0)
    return dbid.gif

def cut_longfilename(detect_files):
    renamefiles = []
    for f in detect_files:
        # if len(f[f.rfind('/')+1:f.rfind('.')]) > 150:
            # print(f[:f.rfind('.')])
        name = f[:f.rfind('.')].replace('&', ' ')     
        if len(name) > 190:
            try:    
                dest = name[:190]+f[f.rfind('.'):]
                os.rename(f, dest)
            except FileExistsError:
                dest = name[:189]+'2'+f[f.rfind('.'):]
                os.rename(f, dest)
            renamefiles.append(dest)
        else:
            renamefiles.append(f)
    return renamefiles

def add_dbids(db, detect_files):
    """새로 발견된 파일들을 DB에 추가하고 필요한 작업을 수행"""
    dbids = [Dbid(f.replace(VIDEO_DIR + '/', '')) for f in detect_files]
    
    result = {
        'OverflowError': [],
        'NotImplementedError': [],
        'FileNotFoundError': [],
        '알수없는에러': [],
        'db_추가': [],
        'converted': [],
        'make_gif': [],
        'make_webp': []
    }

    for dbid in dbids:
        # 파일 유효성 검사
        print(f'파일검사: {dbid.file} ({dbid.type})')
        validation = check_corruptd_video(dbid.file, dbid.type)
        
        if validation in ['OverflowError', 'NotImplementedError', 'FileNotFoundError']:
            result[validation].append(dbid.file)
            continue

        # 메타데이터 추출
        metadata = get_createDate_ffmpeg(dbid.file)
        dbid.showtime = metadata['showtime']
        if metadata['cdate']:
            dbid.cdate = metadata['cdate']

        # TS 파일 변환
        if dbid.type.lower() == 'ts':
            converted = cnv_tsTomp4(dbid)
            result['converted'].append(converted)
            dbid = Dbid(converted)

        # 비디오 메타데이터 추출 및 설정
        video_meta = get_vmeta_ffmpeg(dbid.file)
        for key in ['width', 'height', 'showtime', 'bitrate', 'filesize']:
            setattr(dbid, key, video_meta[key])
        if 'cdate' in video_meta:
            dbid.cdate = video_meta['cdate']

        # 디렉토리 생성
        os.makedirs(dbid.gifdir, exist_ok=True)
        os.makedirs(dbid.webpdir, exist_ok=True)

        # GIF/WEBP 생성
        if video_meta['width'] > video_meta['height']:
            result['make_gif'].append(make_gif(dbid))
            result['make_webp'].append(make_webp(dbid))
        else:
            result['make_gif'].append(make_rotate_gif(dbid))
            result['make_webp'].append(make_rotate_webp(dbid))

        # DB에 저장
        video_meta['dbid'] = dbid.dbid
        video_crud.create_new_video(db, video_meta)
        result['db_추가'].append(dbid.dbid)

    return result



def scan_files(db):
    """영상 파일들을 스캔하고 필요한 작업을 수행하는 메인 함수"""
    start = time.time()

    # 현재 DB에 있는 비디오 목록 가져오기
    videos = video_crud.get_all_videos(db)
    # print('db_len:', len(videos))
    db_files = [Dbid(v.dbid).file for v in videos]
    
    # 실제 HDD의 비디오 파일들과 비교
    hdd_files = scan_hddvideofile()
    # print('hdd_files:', len(hdd_files))
    detect_files = set(hdd_files) - set(db_files)  # 새로 추가된 파일
    del_dbs = set(db_files) - set(hdd_files)       # 삭제된 파일

    # GIF/WEBP 관련 경로 가져오기
    db_dbids = [v.dbid for v in videos]
    gifs = scan_gif([Dbid(d).gifdir for d in db_dbids])
    webps = scan_webp([Dbid(d).webpdir for d in db_dbids]) 

    # 삭제할 GIF/WEBP 파일 찾기
    db_gifs = [Dbid(d).gif for d in db_dbids]
    db_webps = [Dbid(d).webp for d in db_dbids]
    
    del_gifs = set(gifs) - set(db_gifs)
    del_gifs.update([Dbid(f.replace(VIDEO_DIR+'/', '')).gif for f in del_dbs])
    # print('db_update:', len(del_gifs))
    del_webps = set(webps) - set(db_webps)
    del_webps.update([Dbid(f.replace(VIDEO_DIR+'/', '')).webp for f in del_dbs])
    # print('db_update:', len(del_webps))

    # 필요한 정리 작업 수행
    if del_dbs:
        # print('db_delete:', len(del_dbs))
        for db_file in del_dbs:
            video_crud.del_dbid(db, db_file.replace(VIDEO_DIR+'/', ''))
    
    if del_gifs:
        # print('os.remove:', len(del_gifs))
        for gif in del_gifs:
            os.remove(gif)
            
    if del_webps:
        # print('os.remove:', len(del_webps))
        for webp in del_webps:
            os.remove(webp)

    print(f"Scan completed in {time.time() - start:.2f} seconds")

    # 새로 발견된 파일 처리
    if detect_files:
        detect_files = cut_longfilename(detect_files)
        result = add_dbids(db, detect_files)
        result.update({
            'delet_gif': del_gifs,
            'delet_webp': del_webps, 
            'delet_dbids': del_dbs,
            'detect_files': detect_files
        })
        # print(result)
        return result
    # print({
    #     'delete_gif': del_gifs,
    #     'delete_webp': del_webps,
    #     'delete_dbids': del_dbs, 
    #     'detect_files': detect_files
    # })    
    return {
        'delete_gif': del_gifs,
        'delete_webp': del_webps,
        'delete_dbids': del_dbs, 
        'detect_files': detect_files
    }

    
    
    
    
    
    
    
    
    # dbids_name = [i[:i.rfind('.')] for i in dbids]
    # gif_webp = scan_gif_webp(settings.VIDEO_DIR)
    # gif_del = set(gif_webp['gif']) - set(dbids_name)
    # webp_del = set(gif_webp['webp']) - set(dbids_name)
    
    # dbids_scanned_files = scan_dbids(settings.VIDEO_DIR)
    # dbids_del = set(dbids) - set(dbids_scanned_files)
    # dbids_detect = set(dbids_scanned_files) - set(dbids)
    # # print(dbids_detect, '----00-00-0-0')
    
    # dbids_detect_name_100 = []
    # for d in dbids_detect:
        #     dbid = Dbid(d)
    #     # print(dbid.name, '---------------------')
    #     if len(dbid.name) > 100:
        #         src = dbid.file
    #         dest = settings.VIDEO_DIR + dbid.folder + dbid.name[0:99]
    #         os.rename(src, dest)
    #         dbids_detect_name_100.append()
    #     else:
        #         dbids_detect_name_100.append(dbid.dbid)

    # for i in dbids_del:
    #     dbid = Dbid(dbid=i)
    #     video_crud.del_dbid(db=db, dbid=dbid.dbid)
    # for i in gif_del:
        #     _name = i[i.rfind('/')+1:]
    #     _folder = i[:i.rfind('/')]
    #     _filename = settings.VIDEO_DIR + _folder + '/gif/' + _name + '.gif'
    #     # print(_filename)
    #     os.remove(_filename)
    # for i in webp_del:
        #     _name = i[i.rfind('/')+1:]
    #     _folder = i[:i.rfind('/')]
    #     _filename = settings.VIDEO_DIR + _folder + '/webp/' + _name + '.webp'
    #     # print(_filename)
    #     os.remove(_filename)