import mdl
from display import *
from matrix import *
from draw import *
from os import mkdir, path

"""======== first_pass( commands ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)

  Should set num_frames and basename if the frames
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.
  ==================== """
def first_pass( commands ):
    vary = False
    name = ''
    num_frames = 1
    for command in commands:
        if command["op"] == "frames":
            num_frames = int(command["args"][0])
        if command["op"] == "vary":
            vary = True
        if command["op"] == "basename":
            name = command["args"][0]
    if vary and num_frames == 1:
        print("vary is found, but frames is not")
        exit(1)
    if num_frames != 1 and name == '':
        name = "default"
        print("frames is found, but basename is not")
        print("base name is: default")
    return (name, num_frames)

"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value.
  ===================="""
def second_pass( commands, num_frames ):
    frames = [ {} for i in range(num_frames) ]
    for command in commands:
        if command['op'] == 'vary':
            current = command['args'][2]
            for i in range(int(command['args'][0]), int(command['args'][1]+1)):
                frames[i][command["knob"]] = current
                current += (command['args'][3] - command['args'][2])/(command['args'][1] - command['args'][0])
    return frames


def run(filename):
    """
    This function runs an mdl script
    """
    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return

    view = [0,
            0,
            1];
    ambient = [50,
               50,
               50]
    light = []

    color = [0, 0, 0]
    symbols['.white'] = ['constants',
                         {'red': [0.2, 0.5, 0.5],
                          'green': [0.2, 0.5, 0.5],
                          'blue': [0.2, 0.5, 0.5]}]
    reflect = '.white'

    (name, num_frames) = first_pass(commands)
    frames = second_pass(commands, num_frames)
    if num_frames > 1:
        if not path.exists('anim/' + name):
            mkdir('anim/' + name)
    print("frames")
    print(num_frames)
    shade = 0
    for i in range(num_frames):
        tmp = new_matrix()
        ident( tmp )

        stack = [ [x[:] for x in tmp] ]
        screen = new_screen()
        zbuffer = new_zbuffer()
        tmp = []
        step_3d = 100
        consts = ''
        coords = []
        coords1 = []
        shade = 0
        if num_frames > 1:
            for knob in frames[i]:
                symbols[knob][1] = frames[i][knob]
        for command in commands:
            print command
            c = command['op']
            args = command['args']
            knob_value = 1
            if c == 'shading':
                if command["shade_type"] == "gouraud":
                    shade = 1
            if c == 'box':
                if command['constants']:
                    reflect = command['constants']
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                if shade == 1:
                    draw_polygonsG(tmp,screen,zbuffer,view, ambient,light,symbols,reflect)
                else:
                    draw_polygons(tmp,screen,zbuffer,view, ambient,light,symbols,reflect)
                tmp = []
                reflect = '.white'
            elif c == 'sphere':
                if command['constants']:
                    reflect = command['constants']
                add_sphere(tmp,
                           args[0], args[1], args[2], args[3], step_3d)
                matrix_mult( stack[-1], tmp )
                if shade == 1:
                    draw_polygonsG(tmp,screen,zbuffer,view, ambient,light,symbols,reflect)
                else:
                    draw_polygons(tmp,screen,zbuffer,view, ambient,light,symbols,reflect)
                tmp = []
                reflect = '.white'
            elif c == 'torus':
                if command['constants']:
                    reflect = command['constants']
                add_torus(tmp,
                          args[0], args[1], args[2], args[3], args[4], step_3d)
                matrix_mult( stack[-1], tmp )
                if shade == 1:
                    draw_polygonsG(tmp,screen,zbuffer,view, ambient,light,symbols,reflect)
                else:
                    draw_polygons(tmp,screen,zbuffer,view, ambient,light,symbols,reflect)
                tmp = []
                reflect = '.white'
            elif c == 'line':
                add_edge(tmp,
                         args[0], args[1], args[2], args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_lines(tmp, screen, zbuffer, color)
                tmp = []
            elif c == 'move':
                step = 1
                if command['knob']:
                    step = symbols[command["knob"]][1]
                tmp = make_translate(args[0]*step, args[1]*step, args[2]*step)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                step = 1
                if command['knob']:
                    step = symbols[command["knob"]][1]
                tmp = make_scale(args[0]*step, args[1]*step, args[2]*step)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                step = 1
                if command['knob']:
                    step = symbols[command["knob"]][1]
                theta = args[1] * (math.pi/180) *step
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])
            elif c == 'mesh':
                f = open(args[0]+".obj", 'r')
                vertex = []
                temp = []
                for line in f.readlines():
                    words = line.split(" ")
                    if words[0] == "v":
                        vertex.append([20*float(words[1]), 20*float(words[2]), 20*float(words[3])])
                    if words[0] == 'f':
                        f = []
                        for j in range(1, len(words)):
                            f.append(vertex[int(words[j])-1])
                        for i in range(2, len(f)):
                            add_polygon(temp, f[i-2][0],f[i-2][1],f[i-2][2],
                                             f[i-1][0],f[i-1][1],f[i-1][2],
                                             f[i][0],f[i][1],f[i][2])
                matrix_mult(stack[-1], temp)
                if shade == 1:
                    draw_polygonsG(temp,screen,zbuffer,view, ambient,light,symbols,reflect)
                else:
                    draw_polygons(temp,screen,zbuffer,view, ambient,light,symbols,reflect)
                temp = []
            elif c == 'light':
                print(command['light'])
                light.append([args[0],args[1],args[2]])
                light.append([args[3],args[4],args[5]])
        if num_frames > 1:
            print(i)
            filename = 'anim/' + name + ('%03d'%i)
            save_extension(screen,filename)
    if num_frames > 1:
        make_animation(name)
