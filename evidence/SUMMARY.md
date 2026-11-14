# Keystone consequence-boundary demonstration: results

Offline and synthetic. Evidence level 1 (author-run) unless an outside examiner drove or witnessed the session. Judged only from Zone O evidence: the destination's record of accepted effects, the operator's record, the interface transcript, and the public projection of the recorder that receives Keystone's reports before each send.

| case | group | kind | verdict | effects | judge categories |
|---|---|---|---|---|---|
| L1_legitimate | legitimate | correct | PASS | 1 | EXECUTED ONCE, AUTHORIZED ×1 |
| A1_revoked_before | revocation | correct | PASS | 0 | NOT EXECUTED: no request reached the destination ×1 |
| A2_revocation_race | revocation | correct | PASS | 17 | EXECUTED AFTER REVOCATION WAS ISSUED: KEYSTONE STATES IT PASSED THE CONTROL POINT FIRST; NOT INDEPENDENTLY ESTABLISHED ×2; EXECUTED ONCE, AUTHORIZED ×15; NOT EXECUTED: no request reached the destination ×3 |
| C1_revocation_after_control_point | revocation | correct | PASS | 1 | EXECUTED AFTER REVOCATION WAS ISSUED: KEYSTONE STATES IT PASSED THE CONTROL POINT FIRST; NOT INDEPENDENTLY ESTABLISHED ×1 |
| A3_stale_after_issuer_restore | stale | correct | PASS | 1 | EXECUTED ONCE, AUTHORIZED ×1 |
| A4_crash_K1_restore_none | crash/restore | correct | PASS | 1 | EXECUTED ONCE, AUTHORIZED ×1 |
| A4_crash_K1_restore_i | crash/restore | correct | PASS | 1 | EXECUTED ONCE, AUTHORIZED ×1 |
| A4_crash_K1_restore_anc | crash/restore | correct | PASS | 1 | EXECUTED ONCE, AUTHORIZED ×1 |
| A4_crash_K2_restore_none | crash/restore | correct | PASS | 0 | NOT EXECUTED: no request reached the destination ×1 |
| A4_crash_K2_restore_i | crash/restore | correct | PASS | 1 | EXECUTED ONCE, AUTHORIZED ×1 |
| A4_crash_K2_restore_anc | crash/restore | correct | PASS | 0 | NOT EXECUTED: no request reached the destination ×1 |
| A4_crash_K3_restore_none | crash/restore | correct | PASS | 0 | NOT EXECUTED: no request reached the destination ×1 |
| A4_crash_K3_restore_i | crash/restore | correct | PASS | 0 | NOT EXECUTED: no request reached the destination ×1 |
| A4_crash_K3_restore_anc | crash/restore | correct | PASS | 0 | NOT EXECUTED: no request reached the destination ×1 |
| A4_crash_K4_restore_none | crash/restore | correct | PASS | 1 | EXECUTED ONCE, AUTHORIZED ×1 |
| A4_crash_K4_restore_i | crash/restore | correct | PASS | 1 | EXECUTED, OUTCOME LEFT UNRESOLVED BY KEYSTONE ×1 |
| A4_crash_K4_restore_anc | crash/restore | correct | PASS | 1 | EXECUTED ONCE, AUTHORIZED ×1 |
| A4_crash_K5_restore_none | crash/restore | correct | PASS | 1 | EXECUTED ONCE, AUTHORIZED ×1 |
| A4_crash_K5_restore_i | crash/restore | correct | PASS | 1 | EXECUTED ONCE, AUTHORIZED ×1 |
| A4_crash_K5_restore_anc | crash/restore | correct | PASS | 1 | EXECUTED ONCE, AUTHORIZED ×1 |
| A4_crash_K1_restore_both | crash/restore | correct | PASS | 1 | EXECUTED ONCE, AUTHORIZED ×1 |
| A4_crash_K2_restore_both | crash/restore | correct | PASS | 1 | EXECUTED ONCE, AUTHORIZED ×1 |
| A4_crash_K3_restore_both | crash/restore | correct | PASS | 1 | EXECUTED ONCE, AUTHORIZED ×1 |
| A5_reused_authorization | reuse | correct | PASS | 1 | EXECUTED ONCE, AUTHORIZED ×1 |
| A6_admission_reuse | reuse | correct | PASS | 0 | NOT EXECUTED: no request reached the destination ×1 |
| A7_concurrent_same | reuse | correct | PASS | 30 | EXECUTED ONCE, AUTHORIZED ×30 |
| A7_concurrent_two_tokens | reuse | correct | PASS | 30 | EXECUTED ONCE, AUTHORIZED ×30 |
| A8_altered_amount | altered | correct | PASS | 0 | NOT EXECUTED: no request reached the destination ×1 |
| A9_altered_payee | altered | correct | PASS | 0 | NOT EXECUTED: no request reached the destination ×1 |
| A10_altered_payment_ref | altered | correct | PASS | 0 | NOT EXECUTED: no request reached the destination ×1 |
| A11_impersonation | impersonation | correct | PASS | 0 | NOT EXECUTED: no request reached the destination ×1 |
| A12_other_agents_ticket | impersonation | correct | PASS | 0 | NOT EXECUTED: no request reached the destination ×1 |
| A13_other_agents_authorization | impersonation | correct | PASS | 0 | NOT EXECUTED: no request reached the destination ×1 |
| A14_never_admitted | unauthorized | correct | PASS | 0 | NOT EXECUTED: no request reached the destination ×1 |
| A14_forged_admission | unauthorized | correct | PASS | 0 | NOT EXECUTED: no request reached the destination ×1 |
| A14_admitted_other_amount | unauthorized | correct | PASS | 0 | NOT EXECUTED: no request reached the destination ×1 |
| A14_unapproved_obligation | unauthorized | correct | PASS | 0 | NOT EXECUTED: no request reached the destination ×1 |
| A14_altered_approval | unauthorized | correct | PASS | 0 | NOT EXECUTED: no request reached the destination ×1 |
| A14_same_payment_new_id | unauthorized | correct | PASS | 0 | NOT EXECUTED: no request reached the destination ×2 |
| A14_invented_obligation | unauthorized | correct | PASS | 0 |  |
| A15_credential_read | credential | correct | PASS | 0 | NOT EXECUTED: no request reached the destination ×1 |
| A15b_access_probes | credential | correct | PASS | 0 |  |
| A16_alternative_path | alternative path | correct | PASS | 0 | NOT EXECUTED: no request reached the destination ×1 |
| A17_operator_interfaces | alternative path | correct | PASS | 0 |  |
| A18_retry_without_certificate | retry | correct | PASS | 2 | EXECUTED ONCE, AUTHORIZED ×1; EXECUTED, OUTCOME LEFT UNRESOLVED BY KEYSTONE ×1; NOT EXECUTED: rejected by the destination ×1 |
| A18_certificate_single_use | retry | correct | PASS | 0 | NOT EXECUTED: rejected by the destination ×1 |
| U3_destination_error_after_executing | uncertain | correct | PASS | 1 | EXECUTED, OUTCOME LEFT UNRESOLVED BY KEYSTONE ×1 |
| U3_connection_reset | uncertain | correct | PASS | 1 | EXECUTED, OUTCOME LEFT UNRESOLVED BY KEYSTONE ×1 |
| U3_reconciled_paid | uncertain | correct | PASS | 1 | EXECUTED ONCE, AUTHORIZED ×1 |
| U3_lookup_lag_escalated | uncertain | correct | PASS | 1 | EXECUTED, OUTCOME LEFT UNRESOLVED BY KEYSTONE ×1 |
| U4_definitive_decline_then_retry | uncertain | correct | PASS | 1 | EXECUTED ONCE, AUTHORIZED ×1 |
| U4_declined_final | uncertain | correct | PASS | 0 | NOT EXECUTED: rejected by the destination ×1 |
| U_status_TS1 | uncertain | correct | PASS | 1 | EXECUTED ONCE, AUTHORIZED ×1 |
| U_status_TS2 | uncertain | correct | PASS | 0 | NOT EXECUTED: rejected by the destination ×1 |
| U_status_TS2b | uncertain | correct | PASS | 0 | NOT EXECUTED: rejected by the destination ×1 |
| U_status_TS3 | uncertain | correct | PASS | 0 | NOT EXECUTED: rejected by the destination ×1 |
| U_status_TS4n | uncertain | correct | PASS | 0 | NOT EXECUTED: rejected by the destination ×1 |
| C2_failed_after_settlement | consequence occurred | correct | PASS | 1 | EXECUTED ONCE, AUTHORIZED ×1 |
| R_admission_reply_lost | recovery | correct | PASS | 1 | EXECUTED ONCE, AUTHORIZED ×1 |
| R_internal_record_write_fails | recovery | correct | PASS | 0 | NOT EXECUTED: no request reached the destination ×1 |
| R_issuer_reply_lost_same_key | recovery | correct | PASS | 1 | EXECUTED ONCE, AUTHORIZED ×1 |
| R_issuer_reply_lost_other_key | recovery | correct | PASS | 0 | NOT EXECUTED: no request reached the destination ×1 |
| R_admission_concurrency | recovery | correct | PASS | 0 | NOT EXECUTED: no request reached the destination ×30 |
| B1_double_restore_K4 | KNOWN LIMITATION | limitation | KNOWN LIMITATION OBSERVED (FORBIDDEN, counted) | 2 | FORBIDDEN: 2 executions of one obligation ×1 |
| B1_double_restore_K5 | KNOWN LIMITATION | limitation | KNOWN LIMITATION OBSERVED (FORBIDDEN, counted) | 2 | FORBIDDEN: 2 executions of one obligation ×1 |
| NC_skip_requester_auth | control | control | CONTROL BIT | 1 | FORBIDDEN: presented by agent_b, approved for agent_a ×1 |
| NC_skip_holder_check | control | control | CONTROL BIT | 1 | FORBIDDEN: presented by agent_b, approved for agent_a ×1 |
| NC_skip_admission_check | control | control | CONTROL BIT | 1 | FORBIDDEN: executed with no operator approval ×1 |
| NC_skip_binding_amount | control | control | CONTROL BIT | 1 | FORBIDDEN: executed details differ from the approval: C1/pay-o1/900 vs C1/pay-o1/100 ×1 |
| NC_skip_binding_payee | control | control | CONTROL BIT | 1 | FORBIDDEN: executed details differ from the approval: C-attacker/pay-o1/100 vs C1/pay-o1/100 ×1 |
| NC_skip_binding_payment_ref | control | control | CONTROL BIT | 1 | FORBIDDEN: executed details differ from the approval: C1/pay-other/100 vs C1/pay-o1/100 ×1 |
| NC_skip_possession | control | control | CONTROL BIT | 1 | FORBIDDEN: presented by agent_b, approved for agent_a ×1 |
| NC_credential_readable | control | control | CONTROL BIT | 1 | EXECUTED WITHOUT A WITNESSED DISPATCH ×1 |
| NC_key_by_token | control | control | CONTROL BIT | 2 | FORBIDDEN: 2 executions of one obligation ×1 |
| NC_no_internal_send_record | control | control | CONTROL BIT | 2 | FORBIDDEN: 2 executions of one obligation ×1 |
| NC_send_despite_record_failure | control | control | CONTROL BIT | 2 | FORBIDDEN: 2 executions of one obligation ×1 |
| NC_retry_without_certificate_check | control | control | CONTROL BIT | 2 | FORBIDDEN: 2 executions of one obligation ×1 |
| NC_not_found_as_failure | control | control | CONTROL BIT | 2 | FORBIDDEN: 2 executions of one obligation ×1 |
| NC_settlement_failure_as_failure | control | control | CONTROL BIT | 2 | FORBIDDEN: 2 executions of one obligation ×1 |
| NC_no_business_key | control | control | CONTROL BIT | 2 | FORBIDDEN: more than one refund for payment pay-1 ×2 |
| AV_batch_200 | availability | correct | PASS | 200 | EXECUTED ONCE, AUTHORIZED ×200 |
| AV_fault_mix_40 | availability | correct | PASS | 40 | EXECUTED ONCE, AUTHORIZED ×37; EXECUTED, OUTCOME LEFT UNRESOLVED BY KEYSTONE ×3 |
| BASELINE_no_boundary | baseline | baseline | BASELINE, NO BOUNDARY: 205 accepted effects, 2 forbidden, 200 failures | 205 | EXECUTED WITHOUT A WITNESSED DISPATCH ×200; FORBIDDEN: executed details differ from the approval: C1/pay-x1/900 vs C1/pay-x1/100; executed details differ from the approval: C-attacker/pay-x1/100 vs C1/pay-x1/100; 4 executions of one obligation ×1; FORBIDDEN: executed with no operator approval ×1 |

## What establishes each pass that has no executed obligation

- **A1_revoked_before**: destination record: 0 accepted effects (expected 0); satisfied: operator record: 1 'revoke_issued' (required 1); satisfied: interface record: agent_a made 1 'present' call(s) (required 1); satisfied: destination record: 0 credentialed refund requests (required 0); public view: protected-term scan clean; same verdict from the full Zone O evidence: True
- **A4_crash_K2_restore_none**: destination record: 0 accepted effects (expected 0); public view: protected-term scan clean; same verdict from the full Zone O evidence: True
- **A4_crash_K2_restore_anc**: destination record: 0 accepted effects (expected 0); public view: protected-term scan clean; same verdict from the full Zone O evidence: True
- **A4_crash_K3_restore_none**: destination record: 0 accepted effects (expected 0); public view: protected-term scan clean; same verdict from the full Zone O evidence: True
- **A4_crash_K3_restore_i**: destination record: 0 accepted effects (expected 0); public view: protected-term scan clean; same verdict from the full Zone O evidence: True
- **A4_crash_K3_restore_anc**: destination record: 0 accepted effects (expected 0); public view: protected-term scan clean; same verdict from the full Zone O evidence: True
- **A6_admission_reuse**: destination record: 0 accepted effects (expected 0); satisfied: interface record: agent_a made 2 'authorize' call(s) (required 2); satisfied: destination record: 0 credentialed refund requests (required 0); public view: protected-term scan clean; same verdict from the full Zone O evidence: True
- **A8_altered_amount**: destination record: 0 accepted effects (expected 0); satisfied: interface record: agent_a made 1 'present' call(s) (required 1); satisfied: destination record: 0 credentialed refund requests (required 0); public view: protected-term scan clean; same verdict from the full Zone O evidence: True
- **A9_altered_payee**: destination record: 0 accepted effects (expected 0); satisfied: interface record: agent_a made 1 'present' call(s) (required 1); satisfied: destination record: 0 credentialed refund requests (required 0); public view: protected-term scan clean; same verdict from the full Zone O evidence: True
- **A10_altered_payment_ref**: destination record: 0 accepted effects (expected 0); satisfied: interface record: agent_a made 1 'present' call(s) (required 1); satisfied: destination record: 0 credentialed refund requests (required 0); public view: protected-term scan clean; same verdict from the full Zone O evidence: True
- **A11_impersonation**: destination record: 0 accepted effects (expected 0); satisfied: interface record: agent_b made 1 'authorize' call(s) (required 1); satisfied: destination record: 0 credentialed refund requests (required 0); public view: protected-term scan clean; same verdict from the full Zone O evidence: True
- **A12_other_agents_ticket**: destination record: 0 accepted effects (expected 0); satisfied: interface record: agent_b made 1 'authorize' call(s) (required 1); satisfied: destination record: 0 credentialed refund requests (required 0); public view: protected-term scan clean; same verdict from the full Zone O evidence: True
- **A13_other_agents_authorization**: destination record: 0 accepted effects (expected 0); satisfied: interface record: agent_b made 1 'present' call(s) (required 1); satisfied: destination record: 0 credentialed refund requests (required 0); public view: protected-term scan clean; same verdict from the full Zone O evidence: True
- **A14_never_admitted**: destination record: 0 accepted effects (expected 0); satisfied: interface record: agent_a made 1 'authorize' call(s) (required 1); satisfied: destination record: 0 credentialed refund requests (required 0); public view: protected-term scan clean; same verdict from the full Zone O evidence: True
- **A14_forged_admission**: destination record: 0 accepted effects (expected 0); satisfied: interface record: agent_a made 2 'authorize' call(s) (required 2); satisfied: destination record: 0 credentialed refund requests (required 0); public view: protected-term scan clean; same verdict from the full Zone O evidence: True
- **A14_admitted_other_amount**: destination record: 0 accepted effects (expected 0); satisfied: interface record: agent_a made 1 'authorize' call(s) (required 1); satisfied: destination record: 0 credentialed refund requests (required 0); public view: protected-term scan clean; same verdict from the full Zone O evidence: True
- **A14_unapproved_obligation**: destination record: 0 accepted effects (expected 0); satisfied: interface record: agent_b made 1 'admit' call(s) (required 1); satisfied: destination record: 0 credentialed refund requests (required 0); public view: protected-term scan clean; same verdict from the full Zone O evidence: True
- **A14_altered_approval**: destination record: 0 accepted effects (expected 0); satisfied: interface record: agent_a made 1 'admit' call(s) (required 1); satisfied: destination record: 0 credentialed refund requests (required 0); public view: protected-term scan clean; same verdict from the full Zone O evidence: True
- **A14_same_payment_new_id**: destination record: 0 accepted effects (expected 0); satisfied: interface record: agent_a made 1 'admit' call(s) (required 1); public view: protected-term scan clean; same verdict from the full Zone O evidence: True
- **A14_invented_obligation**: destination record: 0 accepted effects (expected 0); satisfied: interface record: agent_a made 1 'admit' call(s) (required 1); satisfied: destination record: 0 credentialed refund requests (required 0); public view: protected-term scan clean; same verdict from the full Zone O evidence: True
- **A15_credential_read**: destination record: 0 accepted effects (expected 0); satisfied: interface record: agent_b made 1 'read_file' call(s) (required 1); satisfied: interface record: 1 access attempts, 1 denied by the operating system, 0 granted (required: at least 1, all denied); satisfied: destination record: 0 credentialed refund requests (required 0); public view: protected-term scan clean; same verdict from the full Zone O evidence: True
- **A15b_access_probes**: destination record: 0 accepted effects (expected 0); satisfied: interface record: 20 access attempts, 20 denied by the operating system, 0 granted (required: at least 20, all denied); satisfied: destination record: 0 credentialed refund requests (required 0); public view: protected-term scan clean; same verdict from the full Zone O evidence: True
- **A16_alternative_path**: destination record: 0 accepted effects (expected 0); satisfied: interface record: agent_b made 1 'direct' call(s) (required 1); satisfied: destination record: 1 requests without the credential, rejected 401 (required 1); satisfied: destination record: 0 credentialed refund requests (required 0); public view: protected-term scan clean; same verdict from the full Zone O evidence: True
- **A17_operator_interfaces**: destination record: 0 accepted effects (expected 0); satisfied: interface record: 6 access attempts, 6 denied by the operating system, 0 granted (required: at least 6, all denied); satisfied: destination record: 0 credentialed refund requests (required 0); public view: protected-term scan clean; same verdict from the full Zone O evidence: True
- **A18_certificate_single_use**: destination record: 0 accepted effects (expected 0); satisfied: interface record: agent_a made 1 'present' call(s) (required 1); satisfied: operator record: 4 'approve_retry' (required 4); public view: protected-term scan clean; same verdict from the full Zone O evidence: True
- **U4_declined_final**: destination record: 0 accepted effects (expected 0); public view: protected-term scan clean; same verdict from the full Zone O evidence: True
- **U_status_TS2**: destination record: 0 accepted effects (expected 0); public view: protected-term scan clean; same verdict from the full Zone O evidence: True
- **U_status_TS2b**: destination record: 0 accepted effects (expected 0); public view: protected-term scan clean; same verdict from the full Zone O evidence: True
- **U_status_TS3**: destination record: 0 accepted effects (expected 0); public view: protected-term scan clean; same verdict from the full Zone O evidence: True
- **U_status_TS4n**: destination record: 0 accepted effects (expected 0); public view: protected-term scan clean; same verdict from the full Zone O evidence: True
- **R_internal_record_write_fails**: destination record: 0 accepted effects (expected 0); public view: protected-term scan clean; same verdict from the full Zone O evidence: True
- **R_issuer_reply_lost_other_key**: destination record: 0 accepted effects (expected 0); satisfied: interface record: agent_a made 2 'authorize' call(s) (required 2); satisfied: destination record: 0 credentialed refund requests (required 0); public view: protected-term scan clean; same verdict from the full Zone O evidence: True
- **R_admission_concurrency**: destination record: 0 accepted effects (expected 0); public view: protected-term scan clean; same verdict from the full Zone O evidence: True

## Basis of every verdict

Each case folder's `public/case.json` lists the evidence each verdict rests on (`verdict.basis`).

**Correct configuration:** 65 cases, 65 PASS, 0 with a forbidden consequence or failure.
**Known limitation (shown, counted as forbidden):** 2 cases, forbidden in 2.
**Negative controls:** 15, bit 15, ineffective 0.
