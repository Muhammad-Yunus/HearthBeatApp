from . import nk
from . import os 
from . import pd 
from . import np
from . import plt 
from . import matplotlib 

class FeatureExtraction():
    def __init__(self, fs = 250, sample_size = 6, pad_size = 15, label_name = ['AF', 'N']):
        self.fs = fs
        self.sample_size = sample_size
        self.label_name = label_name
        self.pad_size = pad_size
        self.X_signal = []
        self.Feature_Data = []
        self.X = []
        self.r_peak_list = []

    def reshape(self, X):
        # reshape input data
        print("\n\n[INFO] Reshape X data...")
        self.Feature_Data = []
        self.X_signal = []
        self.r_peak_list = []
        for item in X :
            self.X_signal.append(item.reshape(2, self.fs*self.sample_size, -1))
        return self.X_signal

    def post_reshape(self, selected_feature_len):
        print("\n\n[INFO] Post Reshape X data...")
        featurs_dfs = pd.concat(self.Feature_Data, axis=1, ignore_index=True)
        self.X = np.array(featurs_dfs.values[:, :self.pad_size*2*selected_feature_len].reshape(-1, self.pad_size*2*selected_feature_len, 1))
        print("[INFO] Matrix shape : ", self.X.shape)

    def list_2_df(self, feature_data):
        data = []
        for i in range(len(feature_data)):
            x = list(feature_data[i][0])
            x.extend(list(feature_data[i][1]))
            data.append(x)
        return pd.DataFrame(data)

    def rr_interval(self):
        print("[INFO] Find R-R Interval for X data...")
        RR_Interval_test = []
        for i in range(len(self.X_signal)) :
            ecg_signal = np.array(self.X_signal[i])
            if len(ecg_signal) > 0:
                r_peaks = []
                try :
                    signal_ch = []
                    r_peaks_ch = []
                    for ch in [0, 1]:
                        _, r_peaks = nk.ecg_peaks(ecg_signal[ch, :, 0], sampling_rate=self.fs)
                        if len(r_peaks['ECG_R_Peaks']) < 2 :
                            raise "R Peaks not found"
                        
                        rr_intv = np.diff(r_peaks['ECG_R_Peaks'])
                        if len(rr_intv) > self.pad_size :
                            print("[INFO] number of peak more than %d : %d" % (self.pad_size, len(rr_intv)))
                        n = len(rr_intv) if len(rr_intv) <= self.pad_size else self.pad_size
                        
                        pad = np.zeros(self.pad_size)
                        pad[0:n] = rr_intv[0:n]
                        signal_ch.append(pad)
                        r_peaks_ch.append(r_peaks)
                    RR_Interval_test.append(signal_ch)
                    self.r_peak_list.append(r_peaks_ch)
                except Exception as e:
                    print("[ERROR] processing data in idx %d  : %s" % (i, e))
        self.Feature_Data.append(self.list_2_df(RR_Interval_test))

    def plot_r_peaks(self, filename, r_peaks, data, root_path, fs=250, label = "Detected R peaks", path="app\static\img-plot"):
        full_path = os.path.join(root_path, path, filename)
        print("[INFO] Saved path : %s" % full_path)

        times = np.arange(data.shape[0], dtype='float') / fs

        ymin = np.min(data)
        ymax = np.max(data)
        alpha = 0.2 * (ymax - ymin)
        ymax += alpha
        ymin -= alpha

        plt.figure(figsize=(20, 5))
        plt.plot(times, data)
        
        plt.vlines([r / fs for r in r_peaks['ECG_R_Peaks']], ymin, ymax,
                color="r",
                linewidth=2)

        plt.title(label)
        plt.xlabel('Time (s)')
        plt.ylabel('Normalized Value')
        plt.grid(True)
        plt.tight_layout()
        plt.show()
        plt.savefig(full_path)
        print("[INFO]  %s saved successfully!" % filename)
        return os.path.join(path, filename).replace("app\\", "\\")

    def qrs_complex(self):
        print("[INFO] find QRS Complex for test dataset...")
        QRS_Complex_test = []
        for i in range(len(self.X_signal)) :
            ecg_signal = np.array(self.X_signal[i])
            if len(ecg_signal) > 0:
                r_peaks = []
                try :
                    signal_ch = []
                    for ch in [0, 1]:
                        _, r_peaks = nk.ecg_peaks(ecg_signal[ch, :, 0], sampling_rate=self.fs)
                        if len(r_peaks['ECG_R_Peaks']) < 2 :
                            raise "R Peaks not found"
                        
                        _, waves_peak = nk.ecg_delineate(ecg_signal[ch, :, 0], r_peaks, sampling_rate=self.fs, method="dwt")
                        r_onsets = waves_peak['ECG_R_Onsets']
                        r_offsets = waves_peak['ECG_R_Offsets']
                        
                        qrs_complex =  np.nan_to_num(np.diff(np.array([r_onsets, r_offsets]).T))[:, 0]
                        
                        n = len(qrs_complex) if len(qrs_complex) <= self.pad_size else self.pad_size
                        pad = np.zeros(self.pad_size)
                        pad[0:n] = qrs_complex[0:n]  
                        signal_ch.append(pad)
                    QRS_Complex_test.append(signal_ch)
                except Exception as e:
                    print("[ERROR] processing data in idx %d  : %s" % (i, e))  
        self.Feature_Data.append(self.list_2_df(QRS_Complex_test))
    
    def qt_interval(self):
        print("[INFO] find QT Interval for test dataset...")
        QT_Interval_test = []
        for i in range(len(self.X_signal)) :
            ecg_signal = np.array(self.X_signal[i])
            if len(ecg_signal) > 0:
                r_peaks = []
                try :
                    signal_ch = []
                    for ch in [0, 1]:
                        _, r_peaks = nk.ecg_peaks(ecg_signal[ch, :, 0], sampling_rate=self.fs)
                        if len(r_peaks['ECG_R_Peaks']) < 2 :
                            raise "R Peaks not found"
                        
                        _, waves_peak = nk.ecg_delineate(ecg_signal[ch, :, 0], r_peaks, sampling_rate=self.fs, method="dwt")
                        r_onsets = waves_peak['ECG_R_Onsets']
                        t_offsets = waves_peak['ECG_T_Offsets']
                        
                        qt_interval =  np.nan_to_num(np.diff(np.array([r_onsets, t_offsets]).T))[:, 0]
                        
                        n = len(qt_interval) if len(qt_interval) <= self.pad_size else self.pad_size
                        pad = np.zeros(self.pad_size)
                        pad[0:n] = qt_interval[0:n]  
                        signal_ch.append(pad)
                    QT_Interval_test.append(signal_ch)
                except Exception as e:
                    print("[ERROR] processing data in idx %d  : %s" % (i, e))  
        self.Feature_Data.append(self.list_2_df(QT_Interval_test))


