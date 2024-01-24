; Copyright 2023 Yevheniya Nosyk
; 
; Licensed under the Apache License, Version 2.0 (the "License");
; you may not use this file except in compliance with the License.
; You may obtain a copy of the License at
; 
;     http://www.apache.org/licenses/LICENSE-2.0
; 
; Unless required by applicable law or agreed to in writing, software
; distributed under the License is distributed on an "AS IS" BASIS,
; WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
; See the License for the specific language governing permissions and
; limitations under the License.

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