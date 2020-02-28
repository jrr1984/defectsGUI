from instrumental import instrument, list_instruments
import threading,time

class Spectrometer(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.last_intensity = []
        self.stopped = False

    def connect(self):
        paramsets = list_instruments()
        self.ccs = instrument(paramsets[0])
        time.sleep(0.1)

    def disconnect(self):
        self.ccs.close()

    def stop(self):
        self.stopped = True

    def measure_spectra(self,num_avg,integ_time):
        self.last_intensity, self.wavelength = self.ccs.take_data(integration_time=integ_time, num_avg=num_avg, use_background=False)
        return self.last_intensity

    def acquire_spectra(self,num_spectra,num_avg,integ_time):
        spectra = []
        for _ in range(num_spectra):
            spectra.append(self.measure_spectra(num_avg,integ_time))
        return spectra

if __name__ == '__main__':
    spec = Spectrometer()
    spec.connect()
    print(spec.measure_spectra(2,'100ms'))
    spec.disconnect()