%% Get EEG Bandpower Means for Each Experiment Task
participant_id = "P02"; % ID of participant whose data you want to process
date = "01-28-23"; % date of experiment session (FORMAT: mm-dd-yy)  
task_names = ["DotsAndNeedles","SeaSpikes","SutureSponge"]; % can just copy from Python

%%% DO NOT EDIT BELOW %%%
for i = 1:numel(task_names)
    task = task_names(i);
    main_dir = 'A:\Training RAS Data Collect'; % stem of folder from which raw data is read
    file = strcat(main_dir,'\',participant_id,'\Emotiv\',date,'\task_',task,'.csv');
    data = readmatrix(file); % get file w / postprocessed data
    data = data(:,5:18); % relevant columns

    sampRate = 128; % sampling rate of your data
    
    chanNr = 1:14; % channel number of your lead
    sampWin = []; % indices of sample points you want to go into analysis. If empty: whole segment is used.
    % compute log spectrum for different frequencies
    if isempty(sampWin)
        [spectra, freq] = spectopo(data(chanNr, :), 0, sampRate,'freqfac', 4, 'plot', 'off');
    else
        [spectra, freq] = spectopo(data(chanNr, sampWin), 0, sampRate,'freqfac', 4, 'plot', 'off');
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
    power_means_theta(:,1) = mean(AllPowerTheta,2);
    power_means_beta_low(:,1) = mean(AllPowerBeta_low,2);
    power_means_beta_high(:,1) = mean(AllPowerBeta_high,2);
    power_means_alpha(:,1) = mean(AllPowerAlpha,2);
    power_means_delta(:,1) = mean(AllPowerDelta,2);
    % power_means_gamma(:,column_count) = mean(AllPowerGamma,2);
    
    % Create a table of (channels x mean power) for each frequency band
    channels = ["AF4"; "F8"; "F4"; "FC6"; "T8"; "P8"; "O2"; "O1"; "P7"; "T7"; "FC5"; "F3"; "F7"; "AF3"]; 
    power_means = [channels power_means_delta power_means_theta power_means_alpha power_means_beta_low power_means_beta_high];
    columns = {'Channel'; 'Delta'; 'Theta'; 'Alpha'; 'Beta_low'; 'Beta_high'};
    power_means = array2table(power_means);
    power_means.Properties.VariableNames = columns; % update columns
    
    % Write table to a single file
    output_dir = strcat(main_dir,'\',participant_id,'\Emotiv\',date,'\');
    writetable(power_means,strcat(output_dir,'task_',task,'_powerMeans.csv'))
end