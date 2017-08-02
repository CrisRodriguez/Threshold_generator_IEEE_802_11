/*
 * Copyright (C) 2013, 2016 Cristian Rodríguez 
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#include <ieee802-11/message_handler.h>

#include <gnuradio/io_signature.h>
#include <gnuradio/block_detail.h>
#include "utils.h"


using namespace gr::ieee802_11;

class message_handler_impl : public message_handler {


public:

	//Constructor
	message_handler_impl(bool log, bool debug) :
	block("message_handler",
			gr::io_signature::make(0, 0, 0),
			gr::io_signature::make(0, 0, 0)),
	d_log(log),
	d_debug(debug),
	d_snr(150) {

	message_port_register_out(pmt::mp("message out"));
	message_port_register_out(pmt::mp("control out"));
	message_port_register_out(pmt::mp("SNR out"));

	message_port_register_in(pmt::mp("app in"));
	set_msg_handler(pmt::mp("app in"), boost::bind(&message_handler_impl::app_in, this, _1));

	}

	void app_in (pmt::pmt_t msg) {
		//when arriving a frame this function is launched.

		if(pmt::is_pair(msg)) {// this must be a pair
			if (!pmt::is_blob(pmt::cdr(msg))) {//The cdr of the pair must be BLOB
				throw std::runtime_error("PMT must be blob");
			}else{
				if (d_debug){
				std::cout << "The cdr is BLOB" << std::endl;
				}				
			}
		} else {
			throw std::invalid_argument("It expects a pair");
			return;
		}

		//Send SNR, which is in the dictionary storaged in the car.
		pmt::pmt_t snrf =pmt::dict_ref(pmt::car(msg), pmt::mp("snr"), pmt::from_double(10));
		message_port_pub(pmt::mp("SNR out"), snrf);


		//Create buf where the BLOB bytes are going to be storaged.
		unsigned char buf[100]={0};
		//Take the size of the BLOB message, which is in the cdr.
		size_t cont=pmt::blob_length(pmt::cdr(msg));
		//Take the BLOB bytes to a Char buf.
		std::memcpy(buf, pmt::blob_data(pmt::cdr(msg)), cont);
		//Print the length of the message
		if (d_debug){
		std::cout << "message length" << cont << std::endl;
		}
		//Convert from char to string.
		std::string aux2(reinterpret_cast<char*>(buf));
		//If cause of the conversion, more data appears, it is erased.
		if(aux2.size()>cont){aux2.erase (cont,2); }
		//The string variable is put in a PMT message, it is not a pair.
		pmt::pmt_t snrf2 = pmt::intern(aux2);

		if (aux2=="fin"){
			//The PMT message is published.
			message_port_pub(pmt::mp("control out"), snrf2);			
		}else{
			//The PMT message is published.
			message_port_pub(pmt::mp("message out"), snrf2);
		}

		if (d_debug)
		{
			//Print message and size.
			std::cout << "The sent message is:" <<aux2<<", its size:" << aux2.size()<<std::endl;
		
		}
			//String variable is cleared.
		aux2.clear();

	}



private:

	bool d_debug;
	bool d_log;
	double d_snr;  // dB
	uint8_t mensaje[1500];



};

message_handler::sptr
message_handler::make(bool log, bool debug) {
	return gnuradio::get_initial_sptr(new message_handler_impl(log, debug));
}

/*
		pmt::pmt_t blob(pmt::cdr(msg));
		const char *aux = reinterpret_cast<const char *>(pmt::blob_data(blob));

		pmt::pmt_t snrf2 = pmt::intern(std::string(aux));
		std::cout << "Es blob " <<std::string(aux)<< std::endl;
		message_port_pub(pmt::mp("message out"), snrf2);
*/
