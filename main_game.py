import sys, time, random, pygame, math, button
from collections import deque 
import cv2 as cv, mediapipe as mp

# Head tracking
mp_drawing = mp.solutions.drawing_utils 
mp_drawing_styles = mp.solutions.drawing_styles # for convenience
mp_face_mesh = mp.solutions.face_mesh # face mesh
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

pygame.init() # init pygame                                   

# Initialize required elements/environment
VID_CAP = cv.VideoCapture(0) #Truy cap camera 0 (camera chinh)

#Set size cua cua so camera
VID_CAP.set(cv.CAP_PROP_FRAME_WIDTH, 1280) #Set width (1280)
VID_CAP.set(cv.CAP_PROP_FRAME_HEIGHT, 720) #Set height (720p)

window_size = (1280, 720)
screen = pygame.display.set_mode(window_size) # set window size cho cua so game

# window_size[0] = width of camera
# window_size[1] = height of camera

# Bird and pipe init
bird_img = pygame.image.load("bird_animation//2.png") # load anh bird
bird_img = pygame.transform.scale(bird_img, (92, 74)) # scale 
bird_frame = bird_img.get_rect() # get frame of bird
bird_frame.center = (window_size[0] // 6, window_size[1] // 2) # set center for bird
pipe_frames = deque() # list of pipe frames, deque is a double-ended queue (FIFO)
pipe_img = pygame.image.load("img//pipe_sprite_single.png")
pipe_starting_template = pipe_img.get_rect() # get frame of pipe
bg_intro = pygame.image.load("img//bg_intro.jpg")
pygame_img = pygame.image.load("img//pygame_logo.png")
pygame_img = pygame.transform.scale(pygame_img, (588/2, 168 / 2))
score_board = pygame.image.load("img//scroreboard.png")
score_board = pygame.transform.scale(score_board, (220, 160))


# BIRB FLY ANIMATION LOOP

# Animation of bird
bird_fly = []
bird_fly.append(pygame.transform.scale(pygame.image.load("bird_animation//1.png"), (92, 74)))
bird_fly.append(bird_img)
bird_fly.append(pygame.transform.scale(pygame.image.load("bird_animation//3.png"), (92, 74)))
bird_fly.append(bird_img)
fly_frame = 0
# Main loop
def bird_fly_animation():
    global fly_frame
    screen.blit(bird_fly[fly_frame], bird_frame)
    fly_frame += 1
    if fly_frame == 4:
        fly_frame = 0



#load image,... for BG
bg = pygame.image.load("img//bg.png").convert() # load anh background
bg_width = bg.get_width() # get width of background
bg_rect = bg.get_rect() # get rectangle of background
scroll = 0
tiles = math.ceil(window_size[0]  / bg_width) + 1 # number of tiles in background

bg_night = pygame.image.load("img//bg_night.png").convert()
bgn_width = bg_night.get_width()
bgn_height = bg_night.get_height()
bgn_rect = bg_night.get_rect()
bg_night = pygame.transform.scale(pygame.image.load("img//bg_night.png"), (math.ceil(bgn_width * window_size[1]/bgn_height), window_size[1]))
tiles_n = math.ceil(window_size[0]  / bgn_width * window_size[1]/bgn_height) + 1



# THONG SO CUA GAME

game_clock = time.time() # thoi gian bat dau game
stage = 1
pipeSpawnTimer = 0 # thoi gian tao cot
space_between_pipes = 230 # khoang cach giua 2 cot tren, duoi
time_between_pipe_spawn = 40 # thoi gian tao cot
dist_between_pipes = 400    # khoang cach giua cac cot theo hang ngang
pipe_velocity = lambda: dist_between_pipes / time_between_pipe_spawn #toc do dich chuyen cua cot
score = 0
didUpdateScore = False

def reset():
    global game_clock, stage, pipeSpawnTimer, time_between_pipe_spawn, dist_between_pipes, score, didUpdateScore
    game_clock = time.time()
    stage = 1
    pipeSpawnTimer = 0
    time_between_pipe_spawn = 40
    score = 0
    didUpdateScore = False



# Background loop
def bg_load():
    global scroll, score
    if math.ceil(score/17)%2 != 0 or score==0:
        #draw scrolling background
        for i in range(0, tiles):
            screen.blit(bg, (i * bg_width + scroll, 0))
    else:
        for i in range(0, tiles_n):
            screen.blit(bg_night, (i * bgn_width + scroll, 0))
    #scroll background
    scroll -= pipe_velocity()
    #reset scroll
    if abs(scroll) > bg_width:
            scroll = 0


# INTRO GAME

pygame.display.set_caption('Flappy Bird Game')   # Tao ten cho cua so chay game
# Set img_intro for game
run = True
while run:
    screen.blit(bg_intro, (0, 0))
    screen.blit(pygame_img, (800, 600)) # set logo pygame
    start_button = button.Button(800, 500, pygame.image.load("img//start_btn.png"), 0.7)
    if start_button.draw(screen):
        break
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()
            sys.exit()
    pygame.display.update()
#pygame.time.wait(5000) # doi 5s

# Music
pygame.mixer.music.load("music//gas2.mp3") # load file nhac
pygame.mixer.music.play(-1) # -1: loop forever, neu muon lap lai file nhac ngan

# STAGE, SCORE TEXT
def score_and_stage():
    global stage, score
    screen.blit(score_board, (0, 0))
    text = pygame.font.SysFont("Helvetica Bold.ttf", 50).render(f'Stage {stage}', True, (0, 0, 0)) 
    tr = text.get_rect()
    tr.center = (100, 50)
    screen.blit(text, tr)
    text = pygame.font.SysFont("Helvetica Bold.ttf", 50).render(f'Score: {score}', True, (0, 0, 0))
    tr = text.get_rect()
    tr.center = (100, 100)
    screen.blit(text, tr)


# GAME OVER
# Thong bao ket thuc game
def game_over():
    VID_CAP.release() # release camera
    cv.destroyAllWindows() # destroy all windows
    pygame.mixer.Channel(1).play(pygame.mixer.Sound("music//sfx_hit.ogg"))
    pygame.mixer.music.load("music//die.mp3")
    pygame.mixer.music.play()
    """
    text = pygame.font.SysFont("Helvetica Bold.ttf", 64).render('Game over!', True, (0, 0, 0)) # font, size, color, text
    tr = text.get_rect() # get rect of text
    tr.center = (window_size[0]/2, window_size[1]/2) # vi tri hien thi thong bao
    screen.blit(text, tr) # hien thi thong bao
"""
    game_over_img = pygame.image.load("img//game_over.png")
    game_over_img = pygame.transform.scale(game_over_img, (game_over_img.get_width() *2 , game_over_img.get_height() * 2))
    tr = game_over_img.get_rect() # get rect of text
    tr.center = (window_size[0]/2, window_size[1]/2) # vi tri hien thi thong bao
    screen.blit(game_over_img, tr) # hien thi thong bao
    pygame.display.update()
    pygame.time.wait(4000) # doi 4s
    """
                Update portions of the screen for software displays
                update(rectangle=None) -> None
                update(rectangle_list) -> None

                This function is like an optimized version of pygame.display.flip() for software displays.
                It allows only a portion of the screen to updated, instead of the entire area.
                If no argument is passed it updates the entire Surface area like pygame.display.flip().

                You can pass the function a single rectangle, or a sequence of rectangles.It is more efficient to pass 
                many rectangles at once than to call update multiple times with single or a partial list of rectangles.
                If passing a sequence of rectangles it is safe to include None values in the list, which will be skipped.
                
                This call cannot be used on pygame.OPENGL displays and will generate an exception.

    """
    pygame.mixer.music.stop() # dung nhac
    f = open("hight_score.txt", "r")
    hight_score = int(f.read())
    f.close()

    result_img = pygame.image.load("img//result.png")
    result_img = pygame.transform.scale(result_img, (result_img.get_width() *3 , result_img.get_height() * 3))
    tr = result_img.get_rect()
    tr.center = (window_size[0]/2, window_size[1]/2)
    screen.blit(result_img, tr) 


    text = pygame.font.SysFont("Helvetica Bold.ttf", 80).render(f'{score}', True, (255, 0, 0)) # font, size, color, text
    tr = text.get_rect() # get rect of text
    tr.center = (window_size[0]/2+50, window_size[1]/2-50) # vi tri hien thi thong bao
    screen.blit(text, tr) # hien thi thong bao


    if score > hight_score:
        hight_score = score
        new_score_img = pygame.image.load("img//new.png")
        new_score_img = pygame.transform.scale(new_score_img, (new_score_img.get_width() *3 , new_score_img.get_height() * 3))
        screen.blit(new_score_img, (window_size[0]/2-120, window_size[1]/2-120))
        f = open("hight_score.txt", "w")
        f.write(str(score))
        f.close()
    
    
    text = pygame.font.SysFont("Helvetica Bold.ttf", 80).render(f'{hight_score}', True, (255, 0, 0)) # font, size, color, text
    tr = text.get_rect() # get rect of text
    tr.center = (window_size[0]/2+50, window_size[1]/2+100) # vi tri hien thi thong bao
    screen.blit(text, tr) # hien thi thong bao

    pygame.display.update()

    pygame.time.wait(8000) # doi 8s
    
    pygame.quit() # quit game
    sys.exit() # exit game


# GAME
with mp_face_mesh.FaceMesh( # tao mot doi tuong FaceMesh
        max_num_faces=1, # so luong face toi da
        refine_landmarks=True, # co the bo sung cac diem nguon
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as face_mesh:
    while True:
        # Check if user quit window
        for event in pygame.event.get(): # lay tat ca cac event trong hang doi voi cua so
            if event.type == pygame.QUIT: # neu nhan nut quit
                VID_CAP.release()
                cv.destroyAllWindows()
                pygame.quit()
                sys.exit()

        # GET FRAME FROM CAMERA
        ret, frame = VID_CAP.read() # lay frame tu camera
        if not ret: # neu khong lay duoc frame
            print("Empty frame, continuing...")
            continue
        
        #BACKGROUND LOOP
        #screen.fill((125, 220, 232)) # fill background with color RGB(125, 220, 232)
        bg_load()

        # FACE MESH
        
        #frame.flags.writeable = False # khong cho phep chinh sua frame
        #frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB) # chuyen frame ve mau RGB
        results = face_mesh.process(frame) 
        #frame.flags.writeable = True # cho phep chinh sua frame
        

# DRAW MESH
        if results.multi_face_landmarks and len(results.multi_face_landmarks) > 0: # neu co nhieu hon 1 face
            # 94 = Tip of nose on face mesh (index of face mesh)
            marker = results.multi_face_landmarks[0].landmark[94].y 
            bird_frame.centery = (marker - 0.5) * 1.5 * window_size[1] + window_size[1]/2 # chuyen toa do y sang toa do y cua bird
            if bird_frame.top < 0: bird_frame.y = 0 # neu bird n
            if bird_frame.bottom > window_size[1]: bird_frame.y = window_size[1] - bird_frame.height # neu cua so nam ngoai duoi cua so

        # Mirror frame, swap axes because opencv != pygame
        #frame = cv.flip(frame, 1).swapaxes(0, 1) # flip frame, swap axes

        # Update pipe positions
        for pf in pipe_frames: # for each pipe frame
            pf[0].x -= pipe_velocity() # chuyen toa do x cua cot tru tren
            pf[1].x -= pipe_velocity() # chuyen toa do x cua cot tru duoi
            #pipe_velocity() la toc to dich chuyen cua cac tru.
            #

        if len(pipe_frames) > 0 and pipe_frames[0][0].right < 0: # neu cot tru tren da cham vao cot tru duoi
            pipe_frames.popleft() # xoa cot tru tren


        # UPDATE SCREEN 

        #pygame.surfarray.blit_array(screen, frame) # hien thi frame camera
        
        bird_fly_animation()
        
        checker = True # checker = True: hien thi cot tru tren

        # DRAW PIPES
        for pf in pipe_frames: # for each pipe frame
            # Check if bird went through to update score
            if pf[0].left <= bird_frame.x <= pf[0].right: # neu cua so nam trong khoang cach cua cot tru
                checker = False # checker = False: khong hien thi cot tru tren
                if not didUpdateScore: # neu chua cap nhat diem
                    score += 1 # cap nhat diem
                    pygame.mixer.Channel(1).play(pygame.mixer.Sound("music//sfx_point.ogg"))
                    didUpdateScore = True # da cap nhat diem 
            # Update screen
            screen.blit(pipe_img, pf[1]) # hien thi cot tru duoi
            screen.blit(pygame.transform.flip(pipe_img, 0, 1), pf[0]) #hien thi cot tru tren
            # pygame.transform.flip(pipe_img, 0, 1): xoay hinh pipe_img 180 do
        if checker: didUpdateScore = False # neu bird nam ngoai khoang cach cua cot tru


        score_and_stage()
        
        
        # Update screen
        pygame.display.flip() #

        """
        pygame.display.flip()
        Update the full display Surface to the screen
        flip() -> None
        This will update the contents of the entire display. If your display mode is using the flags pygame.
        HWSURFACE and pygame.DOUBLEBUF on pygame 1, this will wait for a vertical retrace and swap the surfaces.

        When using an pygame.OPENGL display mode this will perform a gl buffer swap.

        """

        # Check if bird is touching a pipe
        if any([bird_frame.colliderect(pf[0]) or bird_frame.colliderect(pf[1]) for pf in pipe_frames]):
            # Game over
            game_over()

        # Time to add new pipes
        if pipeSpawnTimer == 0: # neu timer = 0 (chua den thoi gian cho phep them cot tru)
            top = pipe_starting_template.copy() # copy cot tru tren
            top.x, top.y = window_size[0], random.randint(120 - 1000 , window_size[1] - 120 - space_between_pipes - 1000) # chon toa do x, y cua cot tru tren
            bottom = pipe_starting_template.copy() # copy cot tru duoi
            bottom.x, bottom.y = window_size[0], top.y + 1000 + space_between_pipes # chon toa do x, y cua cot tru duoi
            pipe_frames.append([top, bottom]) # them toa do cot tru vao pipe_frames

        # Update pipe spawn timer - make it cyclical
        pipeSpawnTimer += 1 
        if pipeSpawnTimer >= time_between_pipe_spawn: pipeSpawnTimer = 0 # reset timer
        # Update stage
        if time.time() - game_clock >= 10: # neu thoi gian chay game >= 10s
            time_between_pipe_spawn *= 5 / 6 # tang thoi gian cho phep them cot tru
            stage += 1 
            game_clock = time.time() # reset game_clock



