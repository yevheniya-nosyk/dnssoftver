$ORIGIN baseline.<your_domain>.
$TTL 600
@       SOA     ns1.baseline.<your_domain>.      hostmaster.baseline.<your_domain>. (
                1 ; serial
                21600      ; refresh after 6 hours
                3600       ; retry after 1 hour
                604800     ; expire after 1 week
                86400 )    ; minimum TTL of 1 day
;NS records
@               IN      NS      ns1
ns1             IN      A       <glue_child> 
ns1             IN      AAAA    <glue_child>
@               IN      NS      ns2
ns2             IN      A       <glue_child> 
ns2             IN      AAAA    <glue_child>

;Baseline test domain
@	         IN      A       <a_record_1>
@       	 IN      A       <a_record_2>
@       	 IN      A       <a_record_3>
@       	 IN      AAAA    <aaaa_record_1>
*            IN      A       <a_record_1>
*            IN      A       <a_record_2>
*            IN      A       <a_record_3>
*            IN      AAAA    <aaaa_record_1>
