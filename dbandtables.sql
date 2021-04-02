CREATE DATABASE apimetadata;

GRANT ALL ON apimetadata.* TO user1@localhost IDENTIFIED BY 'test1';

USE apimetadata;

CREATE TABLE apimetadata.urlpieces (entity VARCHAR(50), provider VARCHAR(50), url VARCHAR(500));

INSERT INTO apimetadata.urlpieces (entity, provider, url) VALUES ("flight", "skyscanner", "http://partners.api.skyscanner.net/apiservices/pricing/v1.0");

INSERT INTO apimetadata.urlpieces (entity, provider, url) VALUES ("events", "yelp", "https://api.yelp.com/v3");

CREATE TABLE apimetadata.airportcities (airportcity VARCHAR(100), country VARCHAR(100), latitude VARCHAR(20), longitude VARCHAR(20));

--loaded data to table apimetadata.airportcities using dbloader.py and /home/akhilesh/TripppIn/data/airports.csv file

CREATE TABLE apimetadata.accesstokens (provider VARCHAR(50), token VARCHAR(500));

INSERT INTO apimetadata.accesstokens (provider, token) VALUES ("yelp", "yAFQwfrfJBPqUX96S2qugFC0EyDAHllzfVdgs9RPLf27keTC3DrC8G00NYJwPLgfU3V3xaTfmClqyhmMIdlST6YWiIFL0WrUO9LXAyhpTIr9LV03XnAlqMsHsFriV3Yx");

CREATE DATABASE algometadata;

GRANT ALL ON algometadata.* TO user1@localhost IDENTIFIED BY 'test1';

USE algometadata;

CREATE TABLE algometadata.categorydna (category VARCHAR(100), chillout INT(10), party INT(10));

--loaded data to table algometadata.categorydna using dbloader.py and /home/akhilesh/TripppIn/data/categories.csv file

ALTER TABLE categorydna ADD weekendtrip INT(10);

ALTER TABLE categorydna ADD explorecountry INT(10);

ALTER TABLE categorydna ADD skiing INT(10);

ALTER TABLE categorydna ADD familyvacation INT(10);
