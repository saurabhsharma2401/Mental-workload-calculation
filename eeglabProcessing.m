function eeglabProcessing(input_file_path, output_file_path)

%     input_file_path = 'C:\Users\EchoLab\Desktop\Necromancer\temp\1.csv'; % folder to which metrics are exported
%     output_file_path = 'C:\Users\EchoLab\Desktop\Necromancer\Data\computed.csv';
    % get a output_file_path and input_file_path
    % Power (total and by channel) for each frequency band
    % Delta (1-4Hz)
    power_all_delta = cell(1,1);
    power_means_delta = zeros(14,1);
    
    % Theta (4-8Hz)
    power_all_theta = cell(1,1);
    power_means_theta = zeros(14,1);
    
    % Alpha (8-12Hz)
    power_all_alpha = cell(1,1);
    power_means_alpha = zeros(14,1);
    
    % Low-beta (12-16Hz)
    power_all_beta_low = cell(1,1);
    power_means_beta_low = zeros(14,1);
    
    % High-beta (16-25Hz)
    power_all_beta_high = cell(1,1);
    power_means_beta_high = zeros(14,1);
    
    % power_all_gamma = cell(1,length(files));
    % power_means_gamma = zeros(14,length(files));
    
    [ALLEEG EEG CURRENTSET ALLCOM] = eeglab; % start EEGLAB (why is this necessary? necessitates the gui)
    % eeglab nogui; % start EEGLAB without gui
    
    % EEGLab Preprocessing by File
    column_count = 1;
    EEG.etc.eeglabvers = '14.1.2'; % this tracks which version of EEGLAB is being used, you may ignore it
    % get data into MATLAB
    dataset = readmatrix(input_file_path);
    dataset = dataset(:,1:14); % drop columns that aren't frequency bands
    dataset = transpose(dataset);
    assignin('base','asdf',dataset);
    % import data into EEGLab (with channel names; note that the name of the matlab array needs to be in parentheses)
    EEG = pop_importdata('dataformat','array','nbchan',14,'data','asdf','srate',128,'pnts',0,'xmin',0,'chanlocs','C:\Users\EchoLab\Desktop\Necromancer\Channel Names\emotiv.ced');
    % EEG.setname=files(j).name();
    EEG = eeg_checkset(EEG);
    % Rereference data
    EEG = pop_reref(EEG, []);
    EEG = eeg_checkset(EEG);
    % High-pass filter (0.5 Hz)
    EEG = pop_eegfiltnew(EEG,'hicutoff',0.5);
    EEG = eeg_checkset(EEG);
    % Cleanline
    EEG = pop_cleanline(EEG, 'bandwidth',2,'chanlist', [1:14],'computepower',1,'linefreqs',[60 120] ,'newversion',0,'normSpectrum',0,'p',0.01,'pad',2,'plotfigures',0,'scanforlines',0,'sigtype','Channels','taperbandwidth',2,'tau',100,'verb',1,'winsize',4,'winstep',1);
    EEG = eeg_checkset(EEG);
    % ICA
    EEG = pop_runica(EEG, 'icatype', 'runica', 'extended', 1, 'interupt', 'off');
    EEG = eeg_checkset(EEG);
    
    % EEG=interface_ADJ(EEG,strcat('report',EEG.setname));
    close();
    
    % compute power bands
    sampRate = 128; % sampling rate of your data
    
    chanNr = 1:14; % channel number of your lead
    sampWin = []; % indices of sample points you want to go into analysis. If empty: whole segment is used.
    % compute log spectrum for different frequencies
    if isempty(sampWin)
        [spectra, freq] = spectopo(EEG.data(chanNr, :), 0, sampRate,'freqfac', 4, 'plot', 'off');
    else
        [spectra, freq] = spectopo(EEG.data(chanNr, sampWin), 0, sampRate,'freqfac', 4, 'plot', 'off');
    end
    
    % delta=1-4, theta=4-8, alpha=8-13, beta=13-30, gamma=30-80
    deltaIdx = find(freq>1 & freq<4);
    thetaIdx = find(freq>4 & freq<8);
    betaIdx_low = find(freq>12 & freq<16);
    betaIdx_high = find(freq>16 & freq<25);
    alphaIdx  = find(freq>8 & freq<12);
    % gammaIdx = find(freq>25 & freq<45);
    
    % Compute absolute power
    AllPowerDelta = 10.^(spectra(:,deltaIdx)/10);
    AllPowerTheta = 10.^(spectra(:,thetaIdx)/10);
    AllPowerBeta_low = 10.^(spectra(:,betaIdx_low)/10);
    AllPowerBeta_high = 10.^(spectra(:,betaIdx_high)/10);
    AllPowerAlpha  = 10.^(spectra(:,alphaIdx)/10);
    % AllPowerGamma = 10.^(spectra(gammaIdx)/10);
    
    % Compute means for each frequency band by channel
    power_means_theta(:,column_count) = mean(AllPowerTheta,2);
    power_means_beta_low(:,column_count) = mean(AllPowerBeta_low,2);
    power_means_beta_high(:,column_count) = mean(AllPowerBeta_high,2);
    power_means_alpha(:,column_count) = mean(AllPowerAlpha,2);
    power_means_delta(:,column_count) = mean(AllPowerDelta,2);
    % power_means_gamma(:,column_count) = mean(AllPowerGamma,2);
    
    
    engagement_index = (power_means_beta_low + power_means_beta_high)./(power_means_theta+power_means_alpha);
    engagement_index = engagement_index.';
    power_means_theta = power_means_theta.';
    power_means_beta_low = power_means_beta_low.';
    power_means_beta_high = power_means_beta_high.';
    power_means_alpha = power_means_alpha.';
    power_means_delta = power_means_delta.';
    
    
    
    
    % Create a table of (channels x mean power) for each frequency band
%     channels = ["AF4"; "F8"; "F4"; "FC6"; "T8"; "P8"; "O2"; "O1"; "P7"; "T7"; "FC5"; "F3"; "F7"; "AF3"]; 
    power_means = [power_means_delta power_means_theta power_means_alpha power_means_beta_low power_means_beta_high engagement_index];
%     columns = {'Channel'; 'Delta'; 'Theta'; 'Alpha'; 'Beta_low'; 'Beta_high'};
    % power_means = array2table(power_means);
    % power_means.Properties.VariableNames = columns; % update columns
%     x = power_means;
    
    % Write table to a single file
    
    dlmwrite(output_file_path,power_means,'-append');
    % writematrix(power_means,strcat(output_dir,task,'_powerMeans.csv'))
    % dlmwrite(strcat(output_dir,'theta_power_means.csv'), power_means_theta(:,:));
    % dlmwrite(strcat(output_dir,'beta_low_power_means.csv'), power_means_beta_low(:,:));
    % dlmwrite(strcat(output_dir,'beta_high_power_means.csv'), power_means_beta_high(:,:));
    % dlmwrite(strcat(output_dir,'alpha_power_means.csv'), power_means_alpha(:,:));
    % dlmwrite(strcat(output_dir,'delta_power_means.csv'), power_means_delta(:,:));
    % % dlmwrite(strcat(main_dir,'gamma_power_means.csv'), power_means_gamma(:,:));
end 
