#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import analysis.Wavelets as Wavelets
import numpy as np
import scipy.signal as signal
import scipy.ndimage as ndimage
import emd


def effectiveFrequency(x,T):
    """

    Parameters
    ----------
    x : 2D array
        Nodes x time.
    T : float
        total time.

    Returns
    -------
    1D float array
        effective frequency.

    """
    return (x[:,-2]-x[:,1])/(2*np.pi*T)
    
def peak_freqs(x,fs=1000,nperseg=4096,noverlap=2048,applySin=True,includeDC=False):
    """
    The peak of the Welch's periodogram.
    Parameters
    ----------
    x : 1D float
        data NxT.
    fs : int
    	sampling frequency
    nperseg : int, optional
        time window in number of samples. The default is 4096.
    noverlap : int, optional
        overlap time in number of samples. The default is 2048.
    applySin : boolean, deafult=True
        apply the sin function before calculate the spectrum
    includeDC : boolean, default=False
        include or not the DC component to find the peak frequency
    Returns
    -------
    f : 1D float array
        list of frequencies.
    Pxx : 2D float array
        Spectrograms: Nodes x frequency
    pfreqs : 1D float array
        frequency peak for each node.

    """
    
    if applySin:
        X=np.sin(x)
    else:
        X=x
    pfreqs=np.zeros((np.shape(x)[0],))
    Pxx=np.zeros((np.shape(x)[0],nperseg//2+1))
    if len(np.shape(x))>1:
        for n in range(np.shape(x)[0]):
            f,Pxx[n,:]=signal.welch(X[n,:],fs=fs,window='hamming',nperseg=nperseg,noverlap=noverlap)
            if includeDC==True:
                pfreqs[n]=f[np.argmax(Pxx[n,:])]
            else:
                pfreqs[n]=f[np.argmax(Pxx[n,1::])]
    else:
        #Single node
        f,Pxx=signal.welch(X,fs=fs,window='hamming',nperseg=nperseg,noverlap=noverlap)
    
    if includeDC==True:
        pfreqs=f[np.argmax(Pxx)]
    else:
        index_max_freq=np.argmax(Pxx)
        if index_max_freq==0:
            index_max_freq==1
        pfreqs=f[index_max_freq+1]
    return f,Pxx,pfreqs

def Npeaks(f,Pxx,N=5,deltaf=5):
    """
    Find the N harmonics
    Parameters
    ----------
    f : 1D float array
        frequencies list.
    Pxx : 1D float array
        Spectrum.
    N : int, optional
        Number of peaks to found. The default is 5.
    deltaf : int, optional
        Number of frequency bins for tolerance between peaks. The default is 5.

    Returns
    -------
    pindex : 1D int array
        Indexes of the peak frequencies in the frequencies list, f.
    pfreqs : 1D float array
        Frequency peaks.

    """
    
    pfreqs=np.zeros((N,np.shape(Pxx)[0]))
    pindex=np.zeros((N,np.shape(Pxx)[0]),dtype=int)
    df=f[1]-f[0]
    delta=int(deltaf/df)+1
    for n in range(np.shape(Pxx)[0]):
        index_peak_one=np.argmax(Pxx[n,:])
        pfreqs[0,n]=f[index_peak_one]
        pindex[0,n]=index_peak_one
        prev_index_peak=index_peak_one
        for j in range(1,N):
                index_peak=np.argmax(Pxx[n,prev_index_peak+delta::])
                pfreqs[j,n]=f[index_peak+prev_index_peak+delta]
                pindex[j,n]=index_peak+prev_index_peak+delta
                prev_index_peak=index_peak+prev_index_peak+delta
    return pindex,pfreqs

def waveletMorlet(x,fs=1000, f_start=0.5,f_end=200, numberFreq=500, omega0=15, correctF=False):
    """
    Wavelet scalogram usign the Morlet mother wavelet

    Parameters
    ----------
    x : 1D float array
        timeserie data.
    fs : fs, optional
        sampling frequency. The default is 1000 Hz.
    f_start : float, optional
        Starting frequency of analysis (larger wavelet scale). 
        This is the most affected scale by the cone of influence.
        The default is 0.5 Hz.
    f_end : float, optional
        End frequency of analyisis. The default is 200 Hz.
    numberFreq : int, optional
        Number of scales (frequency bins). The default is 500.
    omega0 : float, optional
        Central wavelet frequency. Modifies the bandwidth of the scalogram.
        The default is 15.
    correctF : boolean, optional
        If True, the result is normalized by 1/scale(frequency).
        Necessary to identify peaks if the spectrum has 1/f trend.
        The default is False.

    Returns
    -------
    freqs: 1D float array 
        Equivalent frequencies
    scales: 1D float array
        Wavelet scales
    coefs: 2D float array: freqs x len(x) 
        Scalogram coefficients
        Wavelet transform is calculated for each time point.

    """
	
    freqs = np.logspace(np.log10(f_start),np.log10(f_end),numberFreq)
    dt=1/fs
    wavel=Wavelets.Morlet(x,freqs=freqs,dt=dt,omega0=omega0)
    
    coefs=wavel.getnormpower()
    scales=wavel.getscales()
    if correctF:
        for col in range(np.shape(coefs)[1]):
            coefs[:,col]=coefs[:,col]*freqs[:]
    return np.flip(freqs),np.flip(scales),np.flipud(coefs)

def spectrogram(X,fs=1000,nperseg=4096,noverlap=2048):
    """
    Welch spectrogram usign the welch periodograms

    Parameters
    ----------
    X : 1D or 2D float array
        timeseries data. If 2D: N x T
    fs : int
    	sampling frequency
    nperseg : int, optional
        time window in number of samples. The default is 4096.
    noverlap : int, optional
        overlap time in number of samples. The default is 2048.
    
    Returns
    -------
    t: 1D float array 
        center of the time window.
    f: 1D float array
        frequencies list.
    Sxx: 2D or 3D float array: N x len(f) x len(t) 
        Spectrogram with spectral power density units (x^2/Hz). 
    """
    t,f,Sxx=signal.spectrogram(X,fs=fs,nperseg=nperseg,noverlap=noverlap,scaling='density')
    	         
    return t,f,Sxx

def empiricalModeDecomposition(x,fs=1000,f_start=0.2,f_end=200,numberFreq=500):
    #Empirical decomposition (ortogonal signals)
    imf = emd.sift.sift(x)
    #Hilbert-Huang
    freq_range = (f_start, f_end, numberFreq)
    IP, IF, IA = emd.spectra.frequency_transform(imf, fs, 'hilbert')
    hht_f, hht=emd.spectra.hilberthuang(IF, IA, freq_range, mode='amplitude', sum_time=False)
    hht = ndimage.gaussian_filter(hht, 1)
    
    return imf, hht_f, hht
