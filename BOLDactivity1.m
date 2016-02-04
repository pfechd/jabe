function [categorized] = BOLDactivity1(visual_stimuliPath,brain,visual_sphere,tr,images)


clear categorized
clear brain1
clear v1
clear visual_mask
clear antalStimuli
clear in_visual_sphere1
clear response1

%% Detta �r ett fulhack som �r lite mindre h�rdkodat �n orginalscriptet.
%% L�s d�rf�r instruktionerna nedan noga innan du k�r scriptet. 

% Innan du k�r scriptet b�r du k�ra clear all och close all.

% visual_stimuli �r matrisen med onset-tider och inputstyrka. Den ska ha dina
% onset-tider i f�rsta kolumnen och dina input-styrkor i den andra. Den ska
% �ven vara sorterad efter tiderna. Sista onset-tiden ska vara n�r sista
% fokuskorset slutar visas.

% St�ll dig sedan i den mapp d�r du vill ha output. Jag rekommenderar att du har en mapp
% per f�rs�ksperson.


%% Konsten att anropa funktionen:
% visual_stimuli = matrisen med onset-tider och inputstyrka. Den ska ha dina
% onset-tider i f�rsta kolumnen och dina input-styrkor i den andra. Den ska
% �ven vara sorterad efter tiderna. Sista onset-tiden ska vara n�r sista
% fokuskorset slutar visas. D�rf�r b�r din visual_stimuli vara en rad
% l�ngre �n vad du har antal stimuli. 

% tr = tr. Obviously.

% brain1 = vad du nu har d�pt bilden av din hj�rna till n�r du laddade in
% den. 

% images = antal bilder i  din totala tidsserie

% categorize �r output. Varje rad inneh�ller tidsserien f�r en BOLD-kurva,
% (0:or finns bara med f�r att ge alla kurvor samma l�ngd i matrisen) och
% sista kolumnen inneh�ller stimulistyrkan f�r varje kurva. Matrisen �r
% sorterad efter stimulistyrka.


%G�r om onset-tider till image-index.
visual_stimuli = load(strcat(visual_stimuliPath,'.mat'))
fieldNames = fieldnames(visual_stimuli);
visual_stimuli=visual_stimuli.(fieldNames{:,1});
v1 = [visual_stimuli(:,1)/tr]; 
v1 = floor(v1);
v1 = [v1 visual_stimuli(:,2)];

%R�tt format p� hj�rnan
brain1 = load_nii(strcat(brain,'.nii'),[],[],[],[],[],1)
brain1 = brain1.img;
brain1 = double(brain1);

%R�tt format p� masken
visual_mask = load_nii(strcat(visual_sphere,'.nii'),[],[],[],[],[],1)
visual_mask = visual_mask.img;
visual_mask = double(visual_mask);



for i = 1:images % Antalet images i hj�rnan (g�r s�kert att ta reda p� automatiskt men jag orkar inte fundera ut hur. Sorry)
    visual_brain1 = visual_mask.*brain1(:,:,:,i);
visual_brain_time1 = find(visual_brain1);
in_visual_sphere1(i) = mean(visual_brain1(visual_brain_time1)); %R�datakurvan f�r hela sessionen
end

antalStimuli = size(v1,1);

response1 = [];

% Normalize to mean
for i = 1:antalStimuli-1
 numberOfImages = v1(i+1)-v1(i);
response1(i,1:(numberOfImages)) = in_visual_sphere1(v1(i):(v1(i+1)-1))-in_visual_sphere1(v1(i)); %cut out the time series for each response and put them at a row each in response1
end

antalBilder = size(response1,2);

response1 = response1;

% OBS! Samma oavsett vilket område man jobbar med. Kolla så att du har rätt område i response! 

for b1 = 1:antalBilder
    rm1 = find(response1(:,b1));
response1_mean(b1) = mean(response1(rm1,b1));
response1_std(b1) = std(response1(rm1,b1));
end

categorized = [response1(:,1:end-1) visual_stimuli(1:end-1,2)];


categorized = sortrows(categorized,[size(categorized,2)]);



visMean1 = response1_mean;
visStd1 = response1_std;
visMean1(:,1) = 0;
visStd1(:,1) = 0;


save in_visual_sphere1 in_visual_sphere1
save response1 response1
save visMean1 visMean1
save visStd1 visStd1
save categorized categorized

% Plottning

% figure(1)
% p(1:285) = ; % Värde som ligger mitt i aktiveringskurvan
% p(r) = ; % Värde som ligger strax under aktiveringskurvan
% plot(in_visual_mask)
% hold on
% plot(p,'*')
% 
% 
% figure(2)
% g(1:285) = ; % Värde som ligger mitt i aktiveringskurvan
% g(v) = ; % Värde som liggr strax under aktiveringskurvan
% plot(in_visual_mask)
% hold on
% plot(g,'*r')


figure(3)
errorbar(1:antalBilder,visMean1,visStd1)

end
