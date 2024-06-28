<!---
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
--->

**The protocols and software are for reference purposes only and not intended for production usage.**

# Identity Contract Family

## Usages

### Proof of Group Membership

*SIMPLE EXAMPLE*

### Proof of Majority

The Oregon DMV issues a standard driver's license credential for Oregon
residents. The credential includes the driver's name, address, birth date, and
several biometric identifiers (height, weight, eye color, picture). A local
restaurant requires proof that a patron is over the age of 21 before serving
alcohol. The patron would like to present a credential to the restaurant that
proves age without disclosing birth date, address, or name.

Proposed Solution: The Oregon DMV issues a license credential to Alice. This
credential is a JSON blob adhering to the W3C VC standards with the Oregon DMV
signature in the proof block. Alice stores the credential in her identity
contract object. Alice enters a restaurant and orders a drink. The restaurant
requests proof that Alice is over 21. Alice retrieves the license credential
from her identity contract object and submits it to the Age Verification trust
authority (AVTA) contract object. The AVTA contract object identifies the
credential as a license credential (it also accepts passport credentials) and
verifies the integrity of the credential using the signature in the proof
block. If the integrity check is successful, the AVTA contract object checks the
birth date in the credential against the current date and issues a new
credential with the assertion that the bearer is older than 21. The new
credential contains biometric identifiers to associate the credential with a
specific bearer. Alice stores the AVTA credential in her identity contract and
presents it to the restaurant for verification. The restaurant recognizes the
AVTA contract object as a legitimate source of age credentials (that is, it is
part of the restaurant's trust network), verifies the integrity of the
credential, and uses the biometric identifiers to confirm that the credential
belongs to Alice.

### Prescription

This example is based on threats identified in the [Web Of Trust document](https://github.com/WebOfTrustInfo/rwot9-prague/blob/master/final-documents/alice-attempts-abuse-verifiable-credential.md).

A doctor issues prescription to Alice in the form of a credential. The
prescription credential contains information about the drug Alice may use and
also biometric identifiers derived from an identity credential (along the lines
of the driver's lience credential in the previous example) that Alice keeps
stored in her identity contract object. The pharmacy that Alice selects requires
proof that the prescription was written by a legitimate, licensed doctor; that
it was written for Alice; that it has not been filled by another pharmacy; and
that Alice's insurance will cover the cost of the drug identified by the
prescription. *Note that the proposed solution does not address the uniqueness
or insurance aspects of this usage.*

Proposed Solution: The doctor issues a prescription credential to Alice. Alice
selects a pharmacy and finds which trust authorities are required for
verification. She picks a trust authority that represents her local doctors (the
trust authority maintains a list of locally licensed physicians, the LLPTA) and
presents the prescription credential to the trust authority. The LLPTA verifies
the physician's identity and issues a new credential to Alice. Alice presents
the LLPTA credential to the pharmacy who verifies that it was issued by one of
the LLPTA's that it trusts. Along with the credential, Alice presents her
biometric identifiers to confirm that she is, in fact, the subject of the
prescription.

There are several alternatives to verify the doctor's identity. For example, the
pharmacy could retrieve the doctor's credentials explicitly. The approach
described here has two advantages. The first is that the doctor's identity is
hidden from the pharmacy. The second is that the LLPTA may have several ways to
validate the doctor's license to prescribe medicine. The policy for what may be
prescribed may differ from person to person.

### Provenance

### Endorsement

### Reputation (?)

<!--
Bearer of a credential includes a "call back" service, like an mail
address, where a digital asset could be placed, idea is that you must have
access to that location to unpack the asset.
-->

## Contract Objects

### Identity

Store credentials.
List stored credentials.
Create a presentation from the stored credentials.

### Trust Agent

A trust agent contract implements, at a minimum, an operation that takes a list
of credentials as input and outputs a new credential. The configuration of a
trust agent may include specification of schemas for the incoming credentials,
configuration of trusted credential issuers, or other operations to configure
the context of the trust agent.

The primary purpose of the trust agent is to handle delegation of policy.

The primary operation is to take a list of credentials, apply a policy to the
credentials, and then issue a new credential. The policy may be as simple as
validating the schema of the incoming credential. It may also perform a
computation on the credential (for example, computing majority from a
birthdate).

Pre-configured with some policy.
Provided a list of credentials.
Issues a new credential.
