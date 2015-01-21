package com.openhackathon.guacamole;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


public class Connect2OpenHackathon {

	private Logger logger = LoggerFactory.getLogger(Connect2OpenHackathon.class.getClass());
	private URL url = null ;
    private BufferedReader in = null;
    private String urlSTring = null ;
		
	public Connect2OpenHackathon(String urlSTring) throws Exception{
		this.urlSTring = urlSTring;
	}
	
	/*check user withn cookies */
	public String getGuacamoleJSONString(String tokenString) {
		
        String result = null ;
        HttpURLConnection conn = null ;
        
        try {
        	 url = new URL(urlSTring);

        	 HttpURLConnection.setFollowRedirects(false);
        	 conn = (HttpURLConnection) url.openConnection();
        	 
             conn.setRequestMethod("GET");  
             conn.setUseCaches(false);
             conn.setRequestProperty("token", tokenString);
             conn.connect();
             
             int status = conn.getResponseCode();
             
             if (status != 200) {
            	 logger.error("OpenHackathon http reponse code is :" + conn.getResponseCode());
            	 logger.debug("user may have not login , please do it before your request !!!");
            	 return result ;
             }
           
             in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
             String line;
             while ((line = in.readLine()) != null) {
                 result += line;
             }
            
        } catch (Exception e) {
        	logger.error("Exception when connect with OSSLAB to check User Cookies BBB");
            e.printStackTrace();
        }
        finally {
            try {
                if (in != null) {
                    in.close();
                }
                if (conn != null) {
                    conn.disconnect();
				}
            } catch (Exception e2) {
                e2.printStackTrace();
            }
        }
        return result;
    }
	
}

	

