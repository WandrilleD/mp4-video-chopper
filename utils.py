## lots of function definition:

from collections import defaultdict
import os 
import pandas as pd
import numpy as np

def time_to_seconds(t):
    st = t.split(':')
    s = int( st[-1] ) + 60* int( st[-2] ) ## seconds and minutes
    if len(st)==3:
        s += 3600* int( st[0] ) ## hours if they are there
    return s



def overlap( r1 , r2 ):
    ## check if 2 parts overlap
    if r1.source != r2.source:
        return False
    if (r1.start_second < r2.start_second): # r1 starts first 
        return r2.start_second < r1.stop_second # r2 starts before r1 stops
    
    # else: r2 starts first
    return r1.start_second < r2.stop_second # r1 starts before r2 stops

def check_overlap( df ):
    ## check if some parts overlap :
    for i ,row1 in df.iterrows():

        for j ,row2 in df.iterrows():
            if i>=j:
                continue

            if overlap(row1,row2):
                print("Warning: 2 parts are overlapping :")
                print( pd.DataFrame( [ row1 , row2 ] ))
                print('***')
        

def merge_elements(df , i , j):

    row1 = df.loc[i]
    row2 = df.loc[j]

    return pd.concat([ df.drop(index=[i,j]) , 
                              pd.Series((row1.source, np.nan , np.nan , 'OUT',
                                         min( row1.start_second , row2.start_second ),
                                         max( row1.stop_second , row2.stop_second ) ) , 
                                        index = df.columns).to_frame().T
                             ] , ignore_index=True )

def merge_overlapping_elements(df):

    merge = True
    while merge:
        merge=False
        
    
        ## check if some cutout overlap :
        for i ,row1 in df.iterrows():

            for j ,row2 in df.iterrows():
                if j>=i:
                    continue

                if overlap(row1,row2):
                    print(f"merging cutout rows: {i} and {j}" )
                    df = merge_elements(df , i , j)
                    merge = True
                    break
            if merge:
                break
    return df


def associate_parts_and_cutout(df_annot_parts,df_annot_OUT):
    part_to_overlapping_cutout = {}
    ## check overlaps of parts and cutouts:
    for i ,row1 in df_annot_parts.iterrows():
        part_to_overlapping_cutout[i] = []

        for j ,row2 in df_annot_OUT.iterrows():
            if overlap(row1,row2):
                part_to_overlapping_cutout[i].append(j)

    
    df_subparts = pd.DataFrame( columns= df_annot_parts.columns )

    for partI in part_to_overlapping_cutout:
        part = df_annot_parts.loc[ partI ]
        start = part.start_second
        stop = part.stop_second

        for cutoutI in part_to_overlapping_cutout[ partI ]:
            cutout = df_annot_OUT.loc[ cutoutI ]

            ## first check if overlaps is across start or stop of part -> move part start or stop        
            if cutout.start_second <= start:
                ## cut out the beginning 
                start = cutout.stop_second
            elif cutout.stop_second >= stop:
                ## cut out the beginning 
                stop = cutout.start_second
            else: 
                # otherwise a new subpart is formed from the segment of the part before the cutout
                # and the start is updated to the cutout stop
                df_subparts = pd.concat([ df_subparts , 
                                  pd.Series((part.source, np.nan , np.nan , part.destination,
                                             start ,
                                             cutout.start_second ) , 
                                            index = df_annot_parts.columns).to_frame().T
                                 ] , ignore_index=True )

                start = cutout.stop_second
        ## last part :
        df_subparts = pd.concat([ df_subparts , 
                          pd.Series((part.source, np.nan , np.nan , part.destination,
                                     start ,
                                     stop ) , 
                                    index = df_annot_parts.columns).to_frame().T
                         ] , ignore_index=True )

    return df_subparts


def create_commands( df_subparts , prefix = '' ):


    ## now we want to create the commands for the different subparts 
    destination_2_clips = defaultdict(list)
    for i,row in df_subparts.iterrows():

        destination_2_clips[ row.destination ].append( (row.source , 
                                                        format_time(row.start_second), 
                                                        format_time(row.stop_second) ) )



    cmds = {}
    for j,destination in enumerate( destination_2_clips ):
        cmds[destination] = []
        with open(f"destination{j}.clipFiles.txt",'w') as OUT:
            for i, clip in enumerate( destination_2_clips[destination] ) :

                V = clip[0]
                a = clip[1]
                o = clip[2]

                O = prefix + "destination{}_clip{}.mp4".format(j,i)

                #V = V.replace(' ','\ ')
                O = O.replace(' ','\ ')
                cmd = "ffmpeg -ss {} -to {} -i {} {}".format(a,o,V,O)
                cmds[destination].append(cmd)

                print(O , file = OUT)
        ## command to merge files 
        destination_mp4 = destination
        if not destination_mp4.endswith('.mp4'):
            destination_mp4 += '.mp4'

        cmds[destination].append("ffmpeg -f concat -safe 0 -i {} -c copy {}".format(f"destination{j}.clipFiles.txt",
                                                                                    destination_mp4))
        ## cleaning up
        with open(f"destination{j}.clipFiles.txt",'r') as IN:
            for l in IN:
                cmds[destination].append(f'rm {l.strip()}')



    return cmds

def format_time(a):

    hms=[str( a//3600 ),str( (a%3600)//60 ),str( a%60 )]
    for i in range(len(hms)):
        if len(hms[i])==1:
            hms[i] = '0' + hms[i]
    
    return ':'.join( hms )

