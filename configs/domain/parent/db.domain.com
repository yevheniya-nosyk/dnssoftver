$ORIGIN <your_domain>.
$TTL 600
@       SOA     ns1.<your_domain>.      hostmaster.<your_domain>. (
                1 ; serial
                21600      ; refresh after 6 hours
                3600       ; retry after 1 hour
                604800     ; expire after 1 week
                86400 )    ; minimum TTL of 1 day
;NS records
@               IN      NS      ns1
ns1             IN      A       <glue_parent>
ns1             IN      AAAA    <glue_parent>

;Address records
@               IN      A       <a_record>
@               IN      AAAA    <aaaa_record>

;Add subdomains
baseline	    IN	    NS	    ns1.baseline
baseline        IN      NS      ns2.baseline
ns1.baseline    IN	    A	    <glue_child>
ns2.baseline    IN      A       <glue_child>
ns1.baseline    IN      AAAA	<glue_child>
ns2.baseline    IN      AAAA    <glue_child>