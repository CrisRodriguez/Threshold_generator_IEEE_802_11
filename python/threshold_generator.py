#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2016 Cristian Rodríguez
# Research group GRECO, Universidad Distrital Francisco Jose de Caldas, Bogota, Colombia	
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

import numpy as np
import string
import pmt
import struct
import pylab as pl
from gnuradio import gr
from gnuradio import digital

# Variable Global
y =pl.linspace(0.45, 0.745, num=296)
f0=pl.linspace(0, 0, num=296)
aux=pl.linspace(0, 0, num=296)
mp1=[8.3035, 16.6461, 23.2129]
dp1=[1.4856, 3.5105, 1.2788]
mp2=[40.7173, 60.7301, 90.6078]
dp2=[2.7028, 15.0094, 0.7099]
mp3=[-54.1859, -25.5898, -13.8352]
dp3=[0.5453, 9.7560, 0.3756]
mp4=[0.6279, 0.6568, 0.6942]
dp4=[80.2454, 0.0236, 146.9829]
mpy=[0.4854, 0.5020, 0.6185, 0.6861, 0.7127]
dpy=[183.1682, 0.0036, 0.0026, 0.0079, 369.56954]


class threshold_generator(gr.sync_block):
    """
    docstring for block threshold_generator self.multiple = multiple
    """
    def __init__(self, threshold, debug, Rxgain):
        #External Variables Parameters
        self.threshold = threshold
        self.debug = debug
        self.Rxgain=Rxgain
        #Internal Variables PArameters
        self.d_SNR=np.float64(0)
        self.d_FER=np.float64(0)
        self.d_pot=np.float64(0)
        self.d_grx=np.float64(0)

        gr.sync_block.__init__(self,
            name="threshold_generator",
            in_sig=[np.float32],
            out_sig=[])

        self.message_port_register_out(pmt.intern("threshold out"))

        self.message_port_register_in(pmt.intern("SNR in"))
        self.set_msg_handler(pmt.intern("SNR in"), self.SNR_in)  #Funcion SNR_in

        self.message_port_register_in(pmt.intern("FER in"))
        self.set_msg_handler(pmt.intern("FER in"), self.FER_in)  #Funcion SNR_in

    def FER_in(self,msg):
        # Envia mensaje:
        FERv=pmt.cdr(msg)
        FER=pmt.to_float(FERv)
        self.d_FER=np.float64(FER)

    def SNR_in(self,msg):
		# Envia mensaje:
		SNRv=pmt.to_double(msg)

		self.d_SNR=np.float64(SNRv)		
		self.d_grx=np.float64(self.Rxgain)



		# evidencia
		xp1 = self.d_SNR
		xp2 = self.d_FER
		xp3 = 10*np.log10(self.d_pot/ 46);
		xp4 = self.d_grx

		# fusificacion
		u11=1./(1+pl.exp(dp1[0]*(xp1-mp1[0])))
		u12=pl.exp((-0.5*(xp1-mp1[1])**2)/((dp1[1])**2))
		u13=1./(1+pl.exp(dp1[2]*(mp1[2]-xp1)))
		# funciones de pertenencia entrada FER
		u21=1./(1+pl.exp(dp2[0]*(xp2-mp2[0])))
		u22=pl.exp((-0.5*(xp2-mp2[1])**2)/((dp2[1])**2))
		u23=1./(1+pl.exp(dp2[2]*(mp2[2]-xp2)))

		# funciones de pertenencia entrada Potencia
		u31=1./(1+pl.exp(dp3[0]*(xp3-mp3[0])))
		u32=pl.exp((-0.5*(xp3-mp3[1])**2)/((dp3[1])**2))
		u33=1./(1+pl.exp(dp3[2]*(mp3[2]-xp3)))

		# funciones de pertenencia entrada GRx
		u41=1./(1+pl.exp(dp4[0]*(xp4-mp4[0])))
		u42=pl.exp((-0.5*(xp4-mp4[1])**2)/((dp4[1])**2))
		u43=1./(1+pl.exp(dp4[2]*(mp4[2]-xp4)))

		# funciones de pertenencia salida
		# Le pega el universo

		uC1=1./(1+pl.exp(dpy[0]*(y-mpy[0])))
		uC2=pl.exp((-0.5*(y-mpy[1])**2)/((dpy[1])**2))
		uC3=pl.exp((-0.5*(y-mpy[2])**2)/((dpy[2])**2))
		uC4=pl.exp((-0.5*(y-mpy[3])**2)/((dpy[3])**2))
		uC5=1./(1+pl.exp(dpy[4]*(mpy[4]-y)))

		# C?lculo de los antecedentes de las reglas (x1 es Ai Y x2 es Bj) T-Norma m?nimo

		A1=[u11, u31]#1X1X
		Ar1 = min (A1)
		A2= [u11, u21, u32]#112X
		Ar2 = min (A2)
		A3= [u21, u33, u41]#X131
		Ar3 = min (A3)
		A4= [u21, u33, u42]#X132
		Ar4 = min (A4)
		A5= [u21, u33, u43]#X133
		Ar5 = min (A5)
		A6= [u11, u22, u32]#122X
		Ar6 = min (A6)
		A7 =[u11, u22, u33]#123X
		Ar7 = min (A7)
		A8 =[u11, u23, u32]#132X
		Ar8 = min (A8)
		A9 =[u11, u23, u33]#133X
		Ar9 = min (A9)
		A10 =[u12, u21, u31, u41]#2111
		Ar10 = min (A10)
		A11 =[u12,u21,u31,u43]#2113 #CAMBIAR REGLA from 2112
		Ar11 = min (A11)
		A12 =[u12,u21,u33,u42]#2133
		Ar12 = min (A12)
		A13 =[u12,u22,u31,u41]#2211
		Ar13 = min (A13)
		A14 =[u12,u22,u31,u42]#2212
		Ar14 = min (A14)
		A15 =[u12,u22,u32]#222X
		Ar15 = min (A15)
		A16 =[u12,u22,u33,u41]#2231
		Ar16 = min (A16)
		A17 =[u12,u22,u33,u42]#2232
		Ar17= min (A17)
		A18 =[u12,u22,u33,u43]#2233
		Ar18= min (A18)
		A19 =[u12,u23,u31]#231X
		Ar19= min (A19)
		A20 =[u12,u23,u32]#232X
		Ar20= min (A20)
		A21 =[u12,u23,u33]#233X
		Ar21 = min (A21)
		A22 =[u13,u21,u31]#311X
		Ar22 = min (A22)
		A23 =[u13,u21,u41]#31X1
		Ar23 = min (A23)
		A24 =[u13,u21,u42]#31X2
		Ar24 = min (A24)
		A25 =[u13,u21,u43]#31X3
		Ar25 = min (A25)
		A26 =[u13,u22,u41]#32X1
		Ar26 = min (A26)
		A27 =[u13,u22,u42]#32X2
		Ar27 = min (A27)
		A28 =[u13,u22,u43]#32X3
		Ar28 = min (A28)
		A29 =[u13,u23,u41]#33X1
		Ar29 = min (A29)
		A30 =[u13,u23,u33]#333X
		Ar30 = min (A30)

		# C?lculo de la implicaci?n Mamdani para todas las reglas
		for i in range(296):
			r1 = min (Ar1,uC1[i])
			r2 = min (Ar2,uC2[i])
			r3 = min (Ar3,uC3[i])
			r4 = min (Ar4,uC4[i])
			r5 = min (Ar5,uC5[i])
			r6 = min (Ar6,uC3[i])
			r7 = min (Ar7,uC3[i])
			r8 = min (Ar8,uC2[i])
			r9 = min (Ar9,uC3[i])
			r10= min (Ar10,uC3[i])
			r11= min (Ar11,uC4[i])
			r12= min (Ar12,uC4[i])
			r13= min (Ar13,uC2[i])
			r14= min (Ar14,uC2[i])
			r15= min (Ar15,uC3[i])
			r16= min (Ar16,uC3[i])
			r17= min (Ar17,uC3[i])
			r18= min (Ar18,uC4[i])
			r19= min (Ar19,uC1[i])
			r20= min (Ar20,uC2[i])
			r21= min (Ar21,uC3[i])
			r22= min (Ar22,uC3[i])
			r23= min (Ar23,uC3[i])
			r24= min (Ar24,uC4[i])
			r25= min (Ar25,uC5[i])
			r26= min (Ar26,uC3[i])
			r27= min (Ar27,uC4[i])
			r28= min (Ar28,uC5[i])
			r29= min (Ar29,uC3[i])
			r30= min (Ar30,uC3[i])
			f0[i]=max(r1,r2,r3,r4,r5,r6,r7,r8,r9,r10,r11,r12,r13,r14,r15,r16,r17,r18,r19,r20,r21,r22,r23,r24,r25,r26,r27,r28,r29,r30)
			aux[i]=y[i]*f0[i]
		# Defusificacion centroide discreto.
		aux2=sum(aux)/sum(f0)
		self.threshold = float(aux2)
		send_pmt = pmt.make_f32vector(5, ord(' '))  	# Crea PMT vacio
		pmt.f32vector_set(send_pmt, 0, float(xp1))
		pmt.f32vector_set(send_pmt, 1, float(xp2))
		pmt.f32vector_set(send_pmt, 2, float(xp3))
		pmt.f32vector_set(send_pmt, 3, float(xp4))
		pmt.f32vector_set(send_pmt, 4, float(self.threshold))
		# Envia mensaje:
		self.message_port_pub(pmt.intern('threshold out'), pmt.cons(pmt.PMT_NIL, send_pmt))

    def work(self, input_items, output_items):
    	pot = input_items[0]
        potv=pot[0]
        self.d_pot=np.float64(potv)
        return len(input_items[0])


    def set_Rxgain(self,new_val):
        self.Rxgain = new_val
