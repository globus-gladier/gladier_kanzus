#!/usr/bin/env python
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import fabio
from glob import glob
import sys, os, re, fabio, time, argparse, time
from scipy.ndimage import white_tophat, label, gaussian_filter, grey_dilation, find_objects


def finder(q_in, q_out, q_params):
	# get parameters and wait until all processes get their set
	subset = 960
	params = q_params.get()
	time.sleep(5)
	structure = np.ones(9).reshape([3,3])
	while True:
		try:
			# try to get parameters if there are new ones and wait for the other processes to catch theirs
			params = q_params.get_nowait()
			time.sleep(5)
		except:
			pass
		# wait until a filename shows up
		f = q_in.get()
		d = fabio.open(f).data.T
		d[1150:1290,1230:1360] = 0
		d = d[subset:-subset, subset:-subset]
		d = grey_dilation(d, 10)
		spots = label(white_tophat(gaussian_filter(d, params[0]), [params[1], params[1]]) > params[2], structure = structure)
		q_out.put((f, spots[1]))

def findSpots():
	global img
	subset = 480
	structure = np.ones(9).reshape([3,3])
	win4.show()
	d = np.copy(img.image)
	d[1150:1290,1230:1360] = 0
	d = d[subset:-subset, subset:-subset]
	blur = float(blurValue.text())
	minCount = float(threshValue.text())
	filt = int(sizeValue.text())
	# it might be faster to show and hide rectangles instead of adding and removing them each time...
	for i in win4.spot_rect: 
		try:
			img.removeItem(i)
		except:
			pass
	win4.spot_rect = []
	#~ print(blur, filt, minCount)
	spots = label(white_tophat(gaussian_filter(d, blur), [filt, filt]) > minCount, structure = structure)
	var2 = find_objects(spots[0])
	count = 0
	for i in var2:
		y = (i[1].start + i[1].stop) / 2. + subset
		x = (i[0].start + i[0].stop) / 2. + subset
		win4.spot_rect.append(QtGui.QGraphicsRectItem(x - 12.5, y - 12.5, 25., 25.))
		win4.spot_rect[-1].setPen(pg.mkPen('b'))
		img.addItem(win4.spot_rect[-1])
		count += 1
		if count > 1000: 
			print('Too Many Spots. Increase Threshold')
			break
	win4.spot_rect.append(-1)
	#~ print(len(win4.spot_rect))

current_filename = ''
def openFile():
	global current_filename, win4, img
	print(current_filename)
	for i in win4.spot_rect: 
		try:
			img.removeItem(i)
		except:
			pass
	win4.spot_rect = []
	fileLabel.setText(os.path.basename(current_filename))
	fileLabel.setToolTip(current_filename)
	data = fabio.open(current_filename).data.T
	img.setImage(grey_dilation(data, 10), autoLevels = False, autoRange = False, autoHistogramRange = False)
	
	if scaleChk.isChecked():
		m = np.mean(data[data >= 0])
		m = np.max(np.array([m, 1.]))
		img.setLevels(3 * m / 4., 10. * m)
		img.setHistogramRange(3 * m / 4., 10. * m)
	if win4.isVisible():
		findSpots()

def newDir(new_directory = False):
	global N, results, filenames, directory, ins, outs, listAll, listNew, list_process, results_plot
	timer.stop()
	ins = 0
	outs = 0
	listAll = set([])
	listNew = set([])
	while q_in.empty() is not True:
		q_in.get()
	time.sleep(1)
	while q_out.empty() is not True:
		print(q_out.get(), q_out.empty())
	if new_directory is False:
		directory = str(QtGui.QFileDialog.getExistingDirectory(None, 'Select a Folder', '~/home/', QtGui.QFileDialog.ShowDirsOnly))
	else:
		directory = new_directory
	if directory == '': return 0
	results = np.zeros([N, 2]) - 1
	results[:, 0] = np.arange(N)
	filenames = [''] * N
	timer.start(50)


		
def saveFile(save_filename = False):
	if save_filename is False:
		save_filename = QtGui.QFileDialog.getSaveFileName(None, 'Save File Title', directory, selectedFilter='*.txt')
	sf = open(save_filename + '.txt', 'w')
	sf.write('Threshold:' + str(threshValue.text()) + '\n')
	sf.write('Blur:' + blurValue.text() + '\n')
	sf.write('Filter Size:' + sizeValue.text() + '\n')
	sf.write('Min Spots:' + str(hLine.value()) + '\n')
	for i, f in enumerate(filenames):
		if results[i, 1] > hLine.value(): sf.write(f + ' ' + str(results[i, 1]) + '\n')

#!/usr/bin/ python
"""
Import Section
"""
import warnings
warnings.filterwarnings('ignore')
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import sys, os, re, fabio, time, argparse
from collections import OrderedDict
from scipy.ndimage import white_tophat, label, gaussian_filter, grey_dilation, find_objects
from scipy.signal import gauss_spline
from collections import OrderedDict
import urllib
from scipy.signal import argrelextrema

class Circle(pg.EllipseROI):
	def __init__(self, pos, size, **args):
		pg.ROI.__init__(self, pos, size, movable = False, **args)
		self.aspectLocked = True
		self.rotateAllowed = False

class LimitedSizeDict(OrderedDict):
	def __init__(self, *args, **kwds):
		self.size_limit = kwds.pop("size_limit", None)
		OrderedDict.__init__(self, *args, **kwds)
		self._check_size_limit()

	def __setitem__(self, key, value):
		OrderedDict.__setitem__(self, key, value)
		self._check_size_limit()

	def _check_size_limit(self):
		if self.size_limit is not None:
		  while len(self) > self.size_limit:
		    self.popitem(last=False)
"""
Function Definitions
"""
def get_header(header):
	"""
	Extract key parts of image headers from the header of fabio-opened file and return them as a list. A list of wavelength, pixel size, detector distance, the x and y beam center, and exposure time are returned in that order.
	"""
	h = header['_array_data.header_contents']
	wavelength = float(re.findall("Wavelength (\d+[\.]{0,}[\d]{0,}) A", h)[0])
	pixelSize = float(re.findall("Pixel_size (\d+[\.]{0,}[\d]{0,}e-?\d+) m", h)[0])
	detector_distance = float(re.findall("Detector_distance (\d+[\.]{0,}[\d]{0,}) m", h)[0])
	xCenter, yCenter = [int(float(x)) for x in re.findall("Beam_xy \((\d+[\.]{0,}[\d]{0,}), (\d+[\.]{0,}[\d]{0,})\) pixels", h)[0]]
	exposureTime = float(re.findall("Exposure_time (\d+[\.]{0,}[\d]{0,}) s", h)[0])
	return [wavelength, pixelSize, detector_distance, xCenter, yCenter, exposureTime]

def open_file(fn = False):
	"""
	Open an image, perform grey dilation to expand small spots.
	"""	
	global m, d, d2, data, img, label_file, filelist, filename, directory, info, rtoA, rng, header, prevVar2
	# If no filename is given, create an open file dialog to select one
	if fn is False: 
		check_follow.setChecked(False)
		var = str(QtGui.QFileDialog.getOpenFileName(img, 'Select Image File', directory, "CBF files (*.cbf)")) #"MCCD files (*.mccd)"
		if var == '':
			return 'No File Selected'
		filename = var
	else:
		filename = fn
	# Open file and get header
	if filename in dataList.keys():
		d, d2, header, currentInfo = dataList[filename]
		if info[:4] != currentInfo[:4]:
			info = currentInfo
			rtoA = info[2] * np.tan(np.arcsin(info[0] / (2 * rng)) * 2) / info[1]
	else:
		d = fabio.open(filename)
		header = d.header
		currentInfo = get_header(header)
		# If any of the important experimental parameters have changed, recalculate the pixel to resolution conversion, rtoA
		if info[:4] != currentInfo[:4]:
			info = currentInfo
			rtoA = info[2] * np.tan(np.arcsin(info[0] / (2 * rng)) * 2) / info[1]
		d = d.data
		# Temporary fix for newly found bad pixels
		try:
			if beamline == '23i':
				d[1242, 1914] = 0 # for Pilatus
			elif beamline == '23o':
				d[1025, 2080] = 0 # for Eiger
				d[3173, 1542] = 0 # for Eiger
				d[4128, 1040] = 0 # for Eiger
				d[3896, 1029] = 0 # for Eiger
				d[4197, 45] = 0 # for Eiger
				d[203, 4082] = 0 # for Eiger
		except:
			pass
		d2 = grey_dilation(d, 10)
		dataList[filename] = (d, d2, header, info)
	for i in window_spot_find.spot_rect: 
		i.setVisible(False)
	if check_small_spot.isChecked():
		data = d2
	else:
		data = d
	img.setImage(data, autoLevels = False, autoRange = False, autoHistogramRange=False)
	if check_scale.isChecked():
		m = np.mean(data[::10,::10][data[::10,::10] >= 0])
		img.setLevels(3 * m / 4., 10. * m)
		img.setHistogramRange(3 * m / 4., 10. * m)
	label_file.setText(os.path.basename(filename))
	label_file.setToolTip(filename)
	directory = os.path.dirname(filename)
	filelist = list(filter(lambda x: x.endswith('cbf'), os.listdir(directory)))
	filelist.sort()
	if window_beam_center.isVisible():
		beam_center()
	prevVar2 = 0
	if window_spot_find.isVisible():
		find_spots()
	if window_spot_evaluation.isVisible():
		window_spot_evaluation.updateImage()
	if window_view_header.isVisible():
		update_header()

def next_file():
	global filename, filelist
	open_file(os.path.join(directory,filelist[(filelist.index(os.path.basename(filename)) + 1) % len(filelist)]))

def prev_file():
	global filename, filelist
	open_file(os.path.join(directory,filelist[filelist.index(os.path.basename(filename)) - 1]))

def small_update():
	global d, d2, data, img
	if check_small_spot.isChecked():
		data = d2
	else:
		data = d
	img.setImage(data, autoLevels = False, autoRange = False, autoHistogramRange=False)
	if check_scale.isChecked():
		m = np.mean(data[::10,::10][data[::10,::10] >= 0])
		img.setLevels(3 * m / 4., 10. * m)
		img.setHistogramRange(3 * m / 4., 10. * m)

def mouse_move(pos):
	global label_res, rtoA, rng, info, img
	pos = img.getImageItem().mapFromScene(pos)
	x = int(pos.x())
	y = int(pos.y())

	try:
		A = rng[(rtoA > (((x - info[3]) ** 2. + (y - info[4]) ** 2.) ** .5)).argmax() - 1]
		bkg = int(np.median(d[y - 5: y + 5, x - 5: x + 5]))
		if window_spot_find.spot_number == 0:
			label_res.setText(u'Pixel: {:d}, {:d}. Resolution: {:03.2f} \u212b. Counts: {:d}. Background: {:d}'.format(x, y, A, d[y, x], bkg))
		else:
			label_res.setText(u'Pixel: {:d}, {:d}. Resolution: {:03.2f} \u212b. Counts: {:d}. Background: {:d}. Spots: {:d}'.format(x, y, A, d[y, x], bkg, window_spot_find.spot_number))
	except:
		pass

radialInfo = [0, 0, 0, 0, 0]
def radial_math(d, mathRng):
	global circleMask, radialInfo, img, header, info
	currentInfo = get_header(header)
	if radialInfo[:4] != (currentInfo[:4]) or 'circleMask' not in globals():
		radialInfo = currentInfo
		y, x = np.ogrid[:d.shape[0], :d.shape[1]]
		circleMask = ((x - info[3]) ** 2 + (y - info[4]) ** 2) ** .5
		circleMask = info[0] / np.sin(np.arctan(info[1] * circleMask / info[2]) / 2.) / 2.
		circleMask = np.nan_to_num(circleMask)
	# This step will require that a uniform range is required, but this speeds up calculation
	step = np.abs(mathRng[0] - mathRng[1])
	# This should take the mean +- half a step around the desired resolution
	circleStep = (circleMask + step / 2) // step
	rStep = (mathRng + step / 2) // step
	resultsMean = np.zeros_like(rStep)
	data2 = np.ma.array(d, mask = d < 0)
	for i, r in enumerate(rStep):
		try: 	
			resultsMean[i] = data2[circleStep == r].mean()
		except:
			pass
	return resultsMean / currentInfo[5]

def radial_average():
	global d, window_radial_average, radialPlot, p, filename, colorList
	step = .05
	#define range
	x = np.array([0, 0, d.shape[0], d.shape[0]])
	y = np.array([0, d.shape[1], 0, d.shape[1]])
	limit = max(((x - info[3]) ** 2 + (y - info[4]) ** 2) ** .5)
	limit = info[0] / np.sin(np.arctan(info[1] * limit / info[2]) / 2.) / 2.
	radialRng = np.arange(30, limit, -step)
	#call math
	resultsMean = radial_math(d, radialRng)
	if not window_radial_average.isVisible():
		window_radial_average.clear()
		window_radial_average.show()
		p = window_radial_average.addPlot(labels = {'bottom': u'Resolution (\u212b)', 'left': 'Average Counts per Second'})
		p.invertX(True)
		p.addLegend()
		colorList = [[255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 0, 255], [0, 255, 255], [255, 255, 0], [255, 255, 255], [0, 0, 0]]
	radialPlot = p.plot(radialRng, resultsMean, pen = colorList[0], name = os.path.basename(filename))
	colorList.append(colorList.pop(0))

def correlate_ROI():
	global window_beam_center, imgs, d, offset, centerLabel
	filterSize = int(window_beam_center.rois[0].size()[0]) // 2
	y, x = np.ogrid[-filterSize: filterSize, -filterSize: filterSize]
	pos = np.empty([4, 2], dtype = np.int64)
	for i in range(4):
		pos[i] = np.array(window_beam_center.rois[i].pos()) + filterSize
	N = 25
	correlation = np.empty((2 * N, 2 * N))
	data2 = d > (2 * np.median(d[pos[0, 1] + y, pos[0, 0] + x]))
	for r in range(2 * N):
		for c in range(2 * N):
			im0 = data2[r - N + pos[0, 1] + y, c - N + pos[0, 0] + x]
			im1 = np.rot90(data2[r - N + pos[1, 1] + y, c - N + pos[1, 0] + x], 1)
			im2 = np.rot90(data2[r - N + pos[2, 1] + y, c - N + pos[2, 0] + x], 2)
			im3 = np.rot90(data2[r - N + pos[3, 1] + y, c - N + pos[3, 0] + x], 3)
			correlation[r,c] = (im0 * im1 * im2 * im3).mean()
	m = correlation.mean()
	imgs[4].setImage(correlation, levels = (0, correlation.max()))
	offset = np.unravel_index(correlation.argmax(), correlation.shape)
	if max(np.abs(N - offset[1]),np.abs(N - offset[0])) == N:
		centerLabel.setText('Calculation Failed. Try moving or enlarging the green boxes.')
	else:
		centerLabel.setText('Direct Beam Coordinates: X: ' + str(int(info[3] - (N - offset[1]))) + ', Y: ' + str(int(info[4] - (N - offset[0]))) + ', HKL_X: ' + str(1000 * info[1] * (info[4] - (N - offset[0]))) + ', HKL_Y: ' + str(1000 * info[1] * (info[3] - (N - offset[1]))))

from scipy.optimize import curve_fit
def gauss_function(x, a, x0, sigma):
    return a*np.exp(-(x-x0)**2/(2*sigma**2))

val = 0
b = 0
prevBlur = 0
prevFilt = 0
prevVar2 = 0

def greater_than_and_20(a, b):
	return(((a > b) * (a > 20)))

#Improved version of find_spots
def find_spots():
	global d, img, rng, info, val, b, prevFilt, prevBlur, prevVar2
	window_spot_find.show()
	max_spots = int(value_max.text())
	print(d[::10,::10][d[::10,::10] > -1].mean())
	if value_threshold.text() == 'auto':
		threshold  = max(1.1, 1.5 * d[::10,::10][d[::10,::10] > -1].mean())
	else:
		threshold = float(value_threshold.text())
	m = d[::10,::10][d[::10,::10] > -1].mean()
	print(2 - np.log10(m))
	if value_blur.text() == 'auto':
		blur = -.5 * np.log10(d[::10,::10][d[::10,::10] > -1].mean() / 100) + .5
	else:
		blur = float(value_blur.text())
	print(threshold, blur, threshold / blur)
	hat_size = int(value_size.text())
	# hide the boxes to speed
	t0 = time.time()
	for i in window_spot_find.spot_rect: 
		i.setVisible(False)
	while len(window_spot_find.spot_rect) < max_spots:
		window_spot_find.spot_rect.append(QtGui.QGraphicsRectItem(0, 0, 25., 25.))
		window_spot_find.spot_rect[-1].setPen(pg.mkPen('b'))
		window_spot_find.spot_rect[-1].setVisible(False)
		img.addItem(window_spot_find.spot_rect[-1])
	tmp = gaussian_filter(d.astype(np.float), blur)
	tmp = white_tophat(tmp, [hat_size, hat_size]) > threshold
	spots = label(tmp, structure = np.ones([3, 3]))
	var2 = find_objects(spots[0])
	#~ results = spots[1]
	
	var3 = list(var2)
	t00 = time.time()
	if str(value_limit.text()).startswith('auto'):
		#~ print(value_limit.text())
		spot_res = []
		for i in var3:
			x = (i[1].start + i[1].stop) / 2.
			y = (i[0].start + i[0].stop) / 2.
			spot_res.append(rng[(rtoA > (((x - info[3]) ** 2. + (y - info[4]) ** 2.) ** .5)).argmax() - 1])
		val, b = np.histogram(spot_res, rng[::-1])
		#~ try:
			#~ limit = float(str(value_limit.text()).split('auto=')[1])
		#~ except:
			#~ limit = .05
		#~ bad_res = b[:-1][(1.0 * val / val.sum()) > limit]
		#~ b = (b[1:] + b[:-1]) / 2
		#~ b = b[1:]
		b = b[:-1]
		test = argrelextrema(val, greater_than_and_20, order = 5)[0]
		if test.shape != (0,):
			bad_res = b[np.hstack((test - 1, test, test + 1))]
			pg.plot(b, val)
			n = 0
			while n < len(var3[:max_spots]):
				for v in bad_res:
					if np.round(v, 2) == np.round(spot_res[n], 2):
						var3.pop(n)
						spot_res.pop(n)
						n -= 1
						break
				n += 1

	else:
		try:
			limitRng = []
			for i in str(value_limit.text()).replace(' ', '').split(','):
				var = i.split('-')
				try:
					n = var.index('')
					var[n] = 10000 * n
				except:
					pass
				limitRng.append([float(var[0]), float(var[1])])
				limitRng[-1].sort()
			n = 0
			while n < len(var3[:max_spots]):
				x = (var3[n][1].start + var3[n][1].stop) / 2.
				y = (var3[n][0].start + var3[n][0].stop) / 2.
				spot_res = rng[(rtoA > (((x - info[3]) ** 2. + (y - info[4]) ** 2.) ** .5)).argmax() - 1]
				for v in limitRng:
					if v[0] < spot_res <= v[1]:
						var3.pop(n)
						n -= 1
						break
				n += 1
		except:
			pass
	t01 = time.time()
	n = 0
	for n, i in enumerate(var3[:max_spots]):
		x = (i[1].start + i[1].stop) / 2.
		y = (i[0].start + i[0].stop) / 2.
		#TODO: calc res, intensity, size, etc. and filter
		window_spot_find.spot_rect[n].setPos(x - 12.5, y - 12.5)
		window_spot_find.spot_rect[n].setVisible(True)
		#~ if (d[i].max() > threshold) and (d[i].size > 1) and (d[i].size < 150000):
			#~ x = (i[1].start + i[1].stop) / 2.
			#~ y = (i[0].start + i[0].stop) / 2.
			#~ #TODO: calc res, intensity, size, etc. and filter
			#~ window_spot_find.spot_rect.append(QtGui.QGraphicsRectItem(x - 12.5, y - 12.5, 25., 25.))
			#~ window_spot_find.spot_rect[-1].setPen(pg.mkPen('b'))
			#~ img.addItem(window_spot_find.spot_rect[-1])
	t02 = time.time()
	#~ print(t02 - t01, t01 - t00, t00 - t0, t02 - t0)
	window_spot_find.spot_number = n + 1
	#~ window_spot_find.spot_number = len(var3)
	label_res.setText(label_res.text()[:label_res.text().indexOf('. Sp')] + u'. Spots: {:d}'.format(window_spot_find.spot_number))

def set_spot_find_params():
	print('setting server')
	server_name = 'http://bl1ws3:14003/'
	if value_threshold.text() == 'auto':
		print(urllib.urlopen(server_name + 'setSpotFindParams?blur={0:.3f}&hatSize={1:d}&threshold=auto&excludeRes=none'.format(float(value_blur.text()), int(value_size.text()))).read())
	else:
		print(urllib.urlopen(server_name + 'setSpotFindParams?blur={0:.3f}&hatSize={1:d}&threshold={2:.3f}&excludeRes=none'.format(float(value_blur.text()), int(value_size.text()), float(value_threshold.text()))).read())
	

def evaluate_spots():
	s = img.size()
	pos = img.getImageItem().mapFromScene(s.height() * 0.45, s.width() * 0.45)
	x = int(pos.x())
	y = int(pos.y())
	window_spot_evaluation.spotEllipse.setPos(pos)
	window_spot_evaluation.backgroundOutEllipse.show()
	window_spot_evaluation.backgroundInEllipse.show()
	window_spot_evaluation.spotEllipse.show()
	
	window_spot_evaluation.show()

def distance_calc():
	global d, info, offset, distLabel, window_beam_center
	if 'imgs' not in globals():
		beam_center()
	else:
		window_beam_center.show()
		for i, rois in enumerate(window_beam_center.rois):
			rois.show()
	if 'distLabel' not in globals():
		distLabel = pg.LabelItem(justify = 'left')
	distLabel.setText('')
	window_beam_center.addItem(distLabel, row = 3, col = 0, colspan = 3)
	test0 = np.arange(2.95, 3.11, .002)
	data2 = d > (2 * np.median(window_beam_center.rois[0].getArrayRegion(d, img.getImageItem())))
	N = 25
	data = np.roll(np.roll(data2, (N - offset[1]), 1), (N - offset[0]), 0)
	test = radial_math(data, test0)
	imgs[5].setData(x = test0, y = test)
	if max(np.abs(N - offset[1]),np.abs(N - offset[0])) != N:
		try:
			popt, pcov = curve_fit(gauss_function, test0, test, p0 = [4, 3.03, .013])
			actDist = (info[2] * np.tan(np.arcsin(info[0] / (2 * popt[1])) * 2)) / (np.tan(np.arcsin(info[0] / (2 * 3.03)) * 2))
			distLabel.setText(u'Ring Peak: ' + str(round(popt[1], 5)) + u' \u212b. Detector Distance: Nominal: ' + str(round(info[2], 5)) + u', Actual: ' + str(round(actDist, 5)))
		except:
			distLabel.setText('Distance Calculation Failed...')
	else:
		distLabel.setText('Must successfully calculate direct beam coordinates first.')

R = lambda x: np.array([[np.cos(np.pi / 180 * x), -np.sin(np.pi / 180 * x)],[np.sin(np.pi / 180 * x), np.cos(np.pi / 180 * x)]])

def update_center_ROIs(roi):
	global window_beam_center, img, imgs, info
	N = window_beam_center.rois.index(roi)
	ROISize = np.array(roi.size())
	ROIPos = np.array(roi.pos()) - info[3:5] + ROISize / 2
	for i, r in enumerate(window_beam_center.rois):
		if r != roi:
			r.setPos(np.dot(R((i - N) * 90), ROIPos) + info[3:5] - ROISize / 2)
			r.setSize(ROISize)
		im = np.flipud(r.getArrayRegion(d, img.getImageItem()))
		m = im.mean()
		imgs[i].setImage(im, levels = (3 * m / 4., 10. * m))
		

prevROI = None
def make_connection(roi):
	global prevROI
	if roi != prevROI:
		prevROI.sigRegionChanged.disconnect()
		prevROI.sigRegionChangeFinished.disconnect()
		roi.sigRegionChanged.connect(update_center_ROIs)
		roi.sigRegionChangeFinished.connect(correlate_ROI)
		prevROI = roi

def beam_center():
	global img, window_beam_center, d, imgs, prevROI, info, circleMask, centerLabel, offset
	window_beam_center.clear()
	window_beam_center.show()
	try:
		prevROI.sigRegionChanged.disconnect()
		prevROI.sigRegionChangeFinished.disconnect()
	except:
		pass
	imgs = []
	vbs = []
	w1 = window_beam_center.addLayout(row=0, col=0)
	#this will assume a 3.03 angstrom ring for the time being
	#it should actaully read the value in a editable text box to use other values, for aluminum for example
	ringDist = np.int(info[2] * np.tan(np.arcsin(info[0] / (2 * 3.03)) * 2) / (np.sqrt(2) * info[1]))
	ROIsize = np.array(window_beam_center.rois[0].size())
	for i, rois in enumerate(window_beam_center.rois):
		rois.setPos(np.dot(R(i * 90), np.array((ringDist, ringDist))) + info[3:5] - ROIsize / 2)
		rois.show()
		im = np.flipud(rois.getArrayRegion(d, img.getImageItem()))
		m = im.mean()
		im = pg.ImageItem(im, levels = (3 * m / 4., 10. * m))
		imgs.append(im)
		vbs.append(w1.addViewBox(row = (i + i // 2) % 2, col = i // 2, lockAspect = True))
		vbs[-1].addItem(im)
		rois.sigRegionChangeStarted.connect(make_connection)
	rois.sigRegionChanged.connect(update_center_ROIs)
	rois.sigRegionChangeFinished.connect(correlate_ROI)
	prevROI = rois
	corr = w1.addViewBox(row = 0, col = 2, lockAspect = True)
	im = pg.ImageItem(np.zeros([50, 50]))
	corr.addItem(im)
	pw = w1.addPlot(row = 1, col = 2)
	dist = pw.plot()
	imgs.append(im)
	imgs.append(dist)
	centerLabel = pg.LabelItem(justify = 'left')
	window_beam_center.addItem(centerLabel, row = 2, col = 0, colspan = 3)
	correlate_ROI()

circles = []
def adjust_res_rings():
	global img, value_res_ring, circles, rtoA, rng, check_ring
	for c in circles:
		img.removeItem(c[0])
		img.removeItem(c[1])
	circles = []
	for r in value_res_ring.text().split(','):
		resRing = rtoA[(rng < float(r)).argmax()]
		circle = Circle((info[3] - resRing, info[4] - resRing), 2 * resRing, pen = pg.mkPen('r', style=QtCore.Qt.DashLine))
		if check_ring.isChecked():
			text = pg.TextItem(r, color = (255, 0, 0), anchor = (0,1), html = '<b style="color:red;background-color:white">' + r + '</b>')
			text.setPos(info[3] + np.sqrt(2) / 2 * resRing, info[4] - np.sqrt(2)  / 2 * resRing)
		else:
			text = pg.TextItem('')
		circles.append((circle, text))
		img.addItem(circle)
		img.addItem(text)

def update_header():
	h = header['_array_data.header_contents']
	wavelength = float(re.findall("Wavelength (\d+[\.]{0,}[\d]{0,}) A", h)[0])
	pixelSize = float(re.findall("Pixel_size (\d+[\.]{0,}[\d]{0,}e-?\d+) m", h)[0])
	detector_distance = float(re.findall("Detector_distance (\d+[\.]{0,}[\d]{0,}) m", h)[0])
	xCenter, yCenter = [int(float(x)) for x in re.findall("Beam_xy \((\d+[\.]{0,}[\d]{0,}), (\d+[\.]{0,}[\d]{0,})\) pixels", h)[0]]
	exposureTime = float(re.findall("Exposure_time (\d+[\.]{0,}[\d]{0,}) s", h)[0])
	start_angle = float(re.findall("Start_angle (-?\d+[\.]{0,}[\d]{0,}) deg.", h)[0])
	angle_increment = float(re.findall("Angle_increment (\d+[\.]{0,}[\d]{0,}) deg.", h)[0])
	count_cutoff= int(re.findall("Count_cutoff (\d+[\.]{0,}[\d]{0,}) counts", h)[0])
	detector_model = re.findall("Detector: ([A-Za-z0-9 ]+), S/N", h)[0]
	
	text_view_header.setText(\
u"""Wavelength: {0:.3f} \u212b
Detector Distance: {1:.1f} mm
Direct Beam Coordinates: {2:d}, {3:d}
Exposure Time: {4:.2f} s
Pixel Size: {5:d} \u03BCm x {5:d} \u03BCm
Start Angle: {6:.3f} degrees
Angle Step: {7:.3f} degrees
Count Cutoff: {8:d} counts
Detector Model: {9}
""".format(\
wavelength,\
1000. * detector_distance,\
xCenter,\
yCenter,\
exposureTime,\
int(1000000 * pixelSize),\
start_angle,\
angle_increment,\
count_cutoff,
detector_model))
	window_view_header.show()


"""
Qt Configuration
"""			
pg.setConfigOptions(imageAxisOrder='row-major')

app = QtGui.QApplication([])

"""
Adjust Resolution Ring Window
"""
window_resolution_rings = QtGui.QMainWindow()
window_resolution_rings.setWindowTitle('Update Resolution Rings')
layout_res_ring = pg.LayoutWidget()

label_res_ring = QtGui.QLabel()
label_res_ring.setText('Resolution Rings: ')
label_res_ring.setToolTip('Adjust the resolution rings to draw separated by commas.')
value_res_ring = QtGui.QLineEdit()
value_res_ring.setText('10, 4.5, 3.03')

update_rings = QtGui.QPushButton('Update Rings')
update_rings.clicked.connect(adjust_res_rings)

value_res_ring.returnPressed.connect(update_rings.click)

check_ring = QtGui.QCheckBox('Show Resolution?')
check_ring.setChecked(True)

layout_res_ring.addWidget(label_res_ring, row = 0, col = 0)
layout_res_ring.addWidget(value_res_ring, row = 0, col = 1)
layout_res_ring.addWidget(check_ring, row = 1, col = 0)
layout_res_ring.addWidget(update_rings, row = 1, col = 1)

window_resolution_rings.setCentralWidget(layout_res_ring)
window_resolution_rings.hide()

"""
View Header Window
"""
window_view_header = QtGui.QMainWindow()
window_view_header.setWindowTitle('View Header Info')
layout_view_header = pg.LayoutWidget()

text_view_header = QtGui.QTextEdit()
text_view_header.setText('')

layout_view_header.addWidget(text_view_header, row = 0, col = 1)

window_view_header.setCentralWidget(layout_view_header)
window_view_header.hide()

"""
Main Window setup
"""
class MyMainWindow(QtGui.QMainWindow):

    def closeEvent(self, *args, **kwargs):
        global app
        super(QtGui.QMainWindow, self).closeEvent(*args, **kwargs)
        app.closeAllWindows()

window_main = MyMainWindow()

action_exit = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', window_main)        
action_exit.setShortcut('Ctrl+Q')
action_exit.setStatusTip('Exit application')
action_exit.triggered.connect(QtGui.qApp.quit)

openAction = QtGui.QAction('&Open', window_main)        
openAction.setShortcut('Ctrl+O')
openAction.setStatusTip('Open File')
openAction.triggered.connect(open_file)

action_prev = QtGui.QAction('&Previous File', window_main)        
action_prev.setShortcut('Ctrl+P')
action_prev.setStatusTip('Open Previous File')
action_prev.triggered.connect(prev_file)

action_next = QtGui.QAction('&Next File', window_main)        
action_next.setShortcut('Ctrl+N')
action_next.setStatusTip('Open Next File')
action_next.triggered.connect(next_file)

action_average = QtGui.QAction('Perform &Radial Average', window_main)        
action_average.setShortcut('Ctrl+R')
action_average.setStatusTip('Perform Radial Average')
action_average.triggered.connect(radial_average)

action_center = QtGui.QAction('Calculate Direct &Beam Coordinates', window_main)        
action_center.setShortcut('Ctrl+B')
action_center.setStatusTip('Calculate Direct Beam Coordinates')
action_center.triggered.connect(beam_center)

action_distance = QtGui.QAction('Calculate &Detector Distance', window_main)
action_distance.setShortcut('Ctrl+D')
action_distance.setStatusTip('Calculate Detector Distance')
action_distance.triggered.connect(distance_calc)

action_spotfind = QtGui.QAction('Find &Spots', window_main)
action_spotfind.setShortcut('Ctrl+S')
action_spotfind.setStatusTip('Find Spots')
action_spotfind.triggered.connect(find_spots)

action_eval = QtGui.QAction('&Evaluate Single Spots', window_main)
action_eval.setShortcut('Ctrl+E')
action_eval.setStatusTip('Evaluate Single Spots')
action_eval.triggered.connect(evaluate_spots)

action_res_rings = QtGui.QAction('&Adjust Resolution Rings', window_main)
action_res_rings.setShortcut('Ctrl+A')
action_res_rings.setStatusTip('Adjust Resolution Rings')
action_res_rings.triggered.connect(window_resolution_rings.show)

action_view_header = QtGui.QAction('&View Header Info', window_main)
action_view_header.setShortcut('Ctrl+V')
action_view_header.setStatusTip('View Header Info')
action_view_header.triggered.connect(update_header)

menubar = window_main.menuBar()
menu_file = menubar.addMenu('&File')
menu_file.addAction(action_prev)
menu_file.addAction(openAction)
menu_file.addAction(action_next)
menu_file.addAction(action_exit)

menu_tools = menubar.addMenu('&Tools')
menu_tools.addAction(action_average)
menu_tools.addAction(action_center)
menu_tools.addAction(action_distance)
menu_tools.addAction(action_spotfind)
menu_tools.addAction(action_res_rings)
menu_tools.addAction(action_eval)
menu_tools.addAction(action_view_header)

window_main.resize(800, 800)
window_main.setWindowTitle('Small Spots Image Viewer')
#~ window_main.showMaximized()

filelist = []
#~ directory = os.path.expanduser('/mnt/beegfs/')
directory = os.path.expanduser('~')
filelist = list(filter(lambda x: x.endswith('cbf'), os.listdir(directory)))

label_file = QtGui.QLabel()
label_res = QtGui.QLabel()
button_open = QtGui.QPushButton('Open')
button_next = QtGui.QPushButton('Next')
button_prev = QtGui.QPushButton('Prev')
check_scale = QtGui.QCheckBox('Autoscale?')
check_small_spot = QtGui.QCheckBox('Small Spots?')
check_scale.setChecked(True)
check_small_spot.setChecked(True)

img = pg.ImageView()
img.roi.sigRegionChanged.disconnect(img.roiChanged)
img.roi = pg.ROI([1000, 1000], [50, 500], angle = -90, pen=(1,9))
img.roi.addScaleRotateHandle([0.5, 1], [0.5, 0])
img.roi.addScaleRotateHandle([0.5, 0], [0.5, 1])
img.roi.addScaleHandle([0, 0.5], [.5, 0.5])
img.view.addItem(img.roi)
img.roi.hide()
img.roi.sigRegionChanged.connect(img.roiChanged)

layout_main = pg.LayoutWidget()

layout_main.addWidget(button_open, row = 2, col = 1, colspan = 1)
layout_main.addWidget(button_next, row = 2, col = 2, colspan = 1)
layout_main.addWidget(button_prev, row = 2, col = 0, colspan = 1)
layout_main.addWidget(check_scale, row = 2, col = 3, colspan = 1)
layout_main.addWidget(check_small_spot, row = 2, col = 4, colspan = 1)
layout_main.addWidget(label_file, row = 2, col = 6, colspan  = 1)
layout_main.addWidget(img, row = 1, col = 0, colspan = 7)
layout_main.addWidget(label_res, row = 0, col = 0, colspan = 7)

window_main.setCentralWidget(layout_main)

info = [0, 0, 0, 0, 0]

button_open.clicked.connect(open_file)
button_next.clicked.connect(next_file)
button_prev.clicked.connect(prev_file)
check_small_spot.clicked.connect(small_update)
img.scene.sigMouseMoved.connect(mouse_move)

"""
A bad hack to add an inverted greys gradient without modifying the source...(I don't have root)
"""
Gradients = OrderedDict([
    ('waffles', {'ticks': [(0.0, (255, 255, 255, 255)), (1.0, (0, 0, 0, 255))], 'mode': 'rgb'}),
])
gradient = img.ui.histogram.gradient

def changeGradient(var, b = None):
	gradient.restoreState(Gradients['waffles'])

for g in Gradients:
	px = QtGui.QPixmap(100, 15)
	p = QtGui.QPainter(px)
	gradient.restoreState(Gradients[g])
	grad = gradient.getGradient()
	brush = QtGui.QBrush(grad)
	p.fillRect(QtCore.QRect(0, 0, 100, 15), brush)
	p.end()
	gradLabel = QtGui.QLabel()
	gradLabel.setPixmap(px)
	gradLabel.setContentsMargins(1, 1, 1, 1)
	act = QtGui.QWidgetAction(gradient)
	act.setDefaultWidget(gradLabel)
	act.triggered.connect(changeGradient)
	act.name = g
	gradient.menu.addAction(act)

"""
Radial Average Window Setup
"""
window_radial_average = pg.GraphicsWindow(title="Radial Average")
window_radial_average.hide()

"""
Beam Center Window Setup
"""
class BeamCenterWindow(pg.GraphicsWindow):
	"""
	This window needs to have the ROIs from main window so that it can hide them when this window it closed.
	"""
	def __init__(self, **kwds):
		super(BeamCenterWindow, self ).__init__(**kwds)
		self.rois = []
		for i in range(4):
			self.rois.append(pg.ROI([0, 0], [50, 50], pen=[0, 255, 0], snapSize = 2.0, scaleSnap = True, translateSnap = True))
			self.rois[-1].addScaleHandle([1,1], [0, 0], lockAspect=True)
			img.addItem(self.rois[-1])
			self.rois[-1].hide()
	
	def closeEvent(self, event):
		for r in self.rois:
			r.hide()

window_beam_center = BeamCenterWindow(title="Direct Beam Coordinates Calculation")
window_beam_center.hide()

"""
Spot Finder Config Window Setup
"""
class SpotFinderWindow(QtGui.QMainWindow):
	
	def __init__(self, **kwds):
		super(SpotFinderWindow, self ).__init__(**kwds)
		self.spot_rect = []
		self.spot_number = 0
	
	def closeEvent(self, event):
		for i in self.spot_rect: 
			i.setVisible(False)

window_spot_find = SpotFinderWindow()
window_spot_find.setWindowTitle('Spot Finding Parameters')
spotLayout = pg.LayoutWidget()

label_threshold = QtGui.QLabel()
label_threshold.setText('Threshold: ')
label_threshold.setToolTip('Adjust the minimum pixel value that will result in a hit.')
value_threshold = QtGui.QLineEdit()
value_threshold.setText('auto')

label_blur = QtGui.QLabel()
label_blur.setText('Blur: ')
value_blur = QtGui.QLineEdit()
value_blur.setText('1')

label_max_spots = QtGui.QLabel()
label_max_spots.setText('Max Spots: ')
value_max = QtGui.QLineEdit()
value_max.setText('1000')

label_size = QtGui.QLabel()
label_size.setText('Filter Size: ')
value_size = QtGui.QLineEdit()
value_size.setText('6')

label_limit = QtGui.QLabel()
label_limit.setText('Excluded Resolutions: ')
value_limit = QtGui.QLineEdit()
value_limit.setText('None')

update_plot = QtGui.QPushButton('Update Plot')
update_plot.clicked.connect(find_spots)

update_all = QtGui.QPushButton('Update Server')
update_all.clicked.connect(set_spot_find_params)

spotLayout.addWidget(label_threshold, row = 0, col = 0)
spotLayout.addWidget(value_threshold, row = 0, col = 1)

spotLayout.addWidget(label_blur, row = 1, col = 0)
spotLayout.addWidget(value_blur, row = 1, col = 1)

spotLayout.addWidget(label_limit, row = 2, col = 0)
spotLayout.addWidget(value_limit, row = 2, col = 1)

spotLayout.addWidget(label_max_spots, row = 3, col = 0)
spotLayout.addWidget(value_max, row = 3, col = 1)

spotLayout.addWidget(label_size, row = 4, col = 0)
spotLayout.addWidget(value_size, row = 4, col = 1)

spotLayout.addWidget(update_plot, row = 5, col = 0)
spotLayout.addWidget(update_all, row = 5, col = 1)

value_threshold.returnPressed.connect(update_plot.click)
value_blur.returnPressed.connect(update_plot.click)
value_max.returnPressed.connect(update_plot.click)
value_size.returnPressed.connect(update_plot.click)
value_limit.returnPressed.connect(update_plot.click)

window_spot_find.setCentralWidget(spotLayout)
window_spot_find.hide()

"""
Analyze Spot Window Setup
"""
class EvaluateSpotWindow(pg.GraphicsWindow):
	
	def __init__(self, **kwds):
		super(EvaluateSpotWindow, self ).__init__(**kwds)
		self.backgroundOutEllipse = pg.EllipseROI([60, 10], [100, 100], pen=(0,.75*255,255), movable = False)
		self.backgroundInEllipse = pg.EllipseROI([60, 10], [100, 100], pen=(0,.75*255,255), movable = False)
		self.spotEllipse = pg.EllipseROI([0, 0], [50, 50], pen=(255, 0, 0))

		img.addItem(self.backgroundOutEllipse)
		img.addItem(self.backgroundInEllipse)
		img.addItem(self.spotEllipse)

		self.backgroundInEllipse.removeHandle(0)
		self.backgroundInEllipse.removeHandle(0)
		self.backgroundInEllipse.addScaleHandle([-0.5*2.**-0.5 + 0.5, 0.5*2.**-0.5 + 0.5], [0.5, 0.5], lockAspect = True)
		self.backgroundOutEllipse.removeHandle(0)
		self.backgroundOutEllipse.removeHandle(0)
		self.backgroundOutEllipse.addScaleHandle([-0.5*2.**-0.5 + 0.5, 0.5*2.**-0.5 + 0.5], [0.5, 0.5], lockAspect = True)
		
		self.backgroundOutEllipse.hide()
		self.backgroundInEllipse.hide()
		self.spotEllipse.hide()
		
		self.offsetOut = 2
		self.offsetIn = 1
		
		text = ""
		w1 = self.addLayout(row=0, col=0)
		self.label1 = w1.addLabel(text, row=0, col=0)
		self.v1b = w1.addViewBox(row=1, col=0, lockAspect=True)
		self.img1b = pg.ImageItem()
		self.v1b.addItem(self.img1b)
		self.v1b.disableAutoRange('xy')
		self.v1b.autoRange()
		
		self.spotEllipse.sigRegionChanged.connect(self.updateState)
		self.spotEllipse.setAngle(45)
		self.backgroundInEllipse.sigRegionChangeFinished.connect(self.updateOffsetIn)
		self.backgroundOutEllipse.sigRegionChangeFinished.connect(self.updateOffsetOut)
		
		
	def closeEvent(self, event):
		self.backgroundOutEllipse.hide()
		self.backgroundInEllipse.hide()
		self.spotEllipse.hide()
	
	def updateState(self, **kwds):
		state = self.spotEllipse.getState()
		self.backgroundInEllipse.setState(state, update = False)
		self.backgroundInEllipse.scale(self.offsetIn, center = [.5, .5])
		self.backgroundOutEllipse.setState(state, update = False)
		self.backgroundOutEllipse.scale(self.offsetOut, center = [.5, .5])

	def maskCreate(self, x, y, w, h, a, b, t):
		x = x + .5 - w / 2.
		y = y + .5 - h / 2.
		t = (90 - t) / 180. * np.pi
		a = a / 2.
		b = b / 2.
		return ((np.cos(t) ** 2. / a ** 2. + np.sin(t) ** 2. / b ** 2) * x ** 2. + (2. * np.cos(t) * np.sin(t) * (1 / a ** 2 - 1 / b ** 2.)) * x * y + (np.sin(t) ** 2. / a ** 2. + np.cos(t) ** 2. / b ** 2.) * y ** 2.) < 1

	def updateOffsetIn(self, **kwds):
		self.offsetIn = min(self.offsetOut, max(1,(self.backgroundInEllipse.size() / self.spotEllipse.size())[0]))
		self.updateImage()
		
		
	def updateOffsetOut(self, **kwds):
		self.offsetOut = max(self.offsetIn, (self.backgroundOutEllipse.size() / self.spotEllipse.size())[0])
		self.updateImage()

	def updateImage(self, **kwds):    
		pb = self.backgroundOutEllipse.parentBounds()
		tb = int(max(pb.top(), 0) // 1)
		bb = int(max(pb.bottom(), 0) // 1 + 1)
		lb = int(max(pb.left(), 0) // 1)
		rb = int(max(pb.right(), 0) // 1 + 1)
		w = bb - tb
		h = rb - lb
		sOut = self.backgroundOutEllipse.getState()
		sIn = self.backgroundInEllipse.getState()
		ss = self.spotEllipse.getState()
		
		maskOut = np.fromfunction(lambda x, y: self.maskCreate(x, y, w, h, sOut['size'][0], sOut['size'][1], sOut['angle']), (w, h))
		maskIn = np.fromfunction(lambda x, y: self.maskCreate(x, y, w, h, sIn['size'][0], sIn['size'][1], sIn['angle']), (w, h))
		masks = np.fromfunction(lambda x, y: self.maskCreate(x, y, w, h, ss['size'][0], ss['size'][1], ss['angle']), (w, h))
		
		maskb = maskOut ^ maskIn
		view = np.zeros([bb - tb, rb - lb, 3])
		try:
			data = np.ma.array(d[tb:bb, lb:rb], mask = d[tb:bb, lb:rb] < 0)
			view[:,:,0] = data
			view[:,:,1] = data
			view[:,:,2] = data
			m = 10 * max(1, np.median(data))
			transparency = .5
			view[:,:,0] += m * transparency * masks
			view[:,:,1] += .75 * m * transparency * maskb
			view[:,:,2] += m * transparency * maskb
			self.img1b.setImage(view[::-1,:])
			self.img1b.setLevels([0, m])
			self.v1b.autoRange()
			sa = (np.invert(data.mask) * masks).sum()
			sm = np.mean(data[masks])
			si = np.sum(data[masks])
			ba = (np.invert(data.mask) * maskb).sum()
			bm = np.mean(data[maskb])
			bi = np.sum(data[maskb])
			s_b = si - sa * bm
			b = sa * bm
			s_n = s_b / np.sqrt(si)
			self.label1.setText('Signal Stats:<br>\nIntegrated: {0: 6d}, Mean: {1:.4f}, Area: {2: 6d}<br>\nBackground Stats<br>\nIntegrated: {3: 6d}, Mean: {4:.4f}, Area: {5: 6d}<br>\nCombined Stats:<br>\nSignal - Background: {6:.4f}, Background: {8:.4f}, Signal to Noise: {7:.4f}'.format(si, sm, sa, bi, bm, ba, s_b, s_n, b))
		except:
			self.label1.setText('Area Selction Error')
			print('ROI extends outside of the image...Why would you do that?')

