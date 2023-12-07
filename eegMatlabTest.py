import matlab.engine
import glob

# eng = matlab.engine.start_matlab()
# Args - file, folder, task
# file = 'C:/Users/EchoLab/Desktop/RAS Pilot Experiment Code/Raw EEG Data/test1_alec.csv'
# folder = 'C:/Users/EchoLab/Desktop/RAS Pilot Experiment Code/Postprocessed EEG Data'
# task = 'task1'
# eng.eegLabProcessingFunc(file,folder,task,nargout=0)

# print("[MAIN]: Starting MATLAB...")
eng = matlab.engine.start_matlab()
# folder = "C:/Users/EchoLab/Desktop/RAS Pilot Experiment Code/Raw EEG Data/"
# eegRecordingName = "test5_eegStream"
# path = folder + '/' + eegRecordingName + '*.csv' # wildcard to locate recording 
# file = glob.glob(path)[0] # raw EEG stream from recording
# file = file.replace('\\','/')
# print(file)
eng.eeglabProcessing('C:\\Users\\EchoLab\\Desktop\\Necromancer\\temp\\1.csv','C:\\Users\\EchoLab\\Desktop\\Necromancer\\Data\\computed.csv',nargout=0) # runs EEGLab on task data; saves to a file named "[task]_eegPowerMeans.csv" in participant's folder
print("[DEBUG]: EEG band power means computed.")