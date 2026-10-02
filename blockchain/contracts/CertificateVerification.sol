// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract CertificateVerification {

    struct Certificate {
        string certificateId;
        string studentName;
        string course;
        string institution;
        string certificateHash;
        uint256 issueDate;
        address issuer;
        bool exists;
        bool revoked;
    }

    mapping(string => Certificate) private certificates;

    address public owner;

    event CertificateIssued(
        string certificateId,
        string certificateHash,
        address issuer
    );

    event CertificateRevoked(
        string certificateId
    );

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(
            msg.sender == owner,
            "Only owner can perform this action"
        );
        _;
    }

    function issueCertificate(
        string memory _certificateId,
        string memory _studentName,
        string memory _course,
        string memory _institution,
        string memory _certificateHash,
        uint256 _issueDate
    ) public onlyOwner {

        require(
            !certificates[_certificateId].exists,
            "Certificate already exists"
        );

        certificates[_certificateId] = Certificate({
            certificateId: _certificateId,
            studentName: _studentName,
            course: _course,
            institution: _institution,
            certificateHash: _certificateHash,
            issueDate: _issueDate,
            issuer: msg.sender,
            exists: true,
            revoked: false
        });

        emit CertificateIssued(
            _certificateId,
            _certificateHash,
            msg.sender
        );
    }

    function verifyCertificate(
        string memory _certificateId,
        string memory _certificateHash
    )
        public
        view
        returns (
            bool isValid,
            bool isRevoked
        )
    {
        Certificate memory certificate =
            certificates[_certificateId];

        if (!certificate.exists) {
            return (false, false);
        }

        if (certificate.revoked) {
            return (false, true);
        }

        if (
            keccak256(
                bytes(certificate.certificateHash)
            )
            ==
            keccak256(
                bytes(_certificateHash)
            )
        ) {
            return (true, false);
        }

        return (false, false);
    }

    function getCertificate(
        string memory _certificateId
    )
        public
        view
        returns (
            string memory certificateId,
            string memory studentName,
            string memory course,
            string memory institution,
            string memory certificateHash,
            uint256 issueDate,
            address issuer,
            bool revoked
        )
    {
        require(
            certificates[_certificateId].exists,
            "Certificate not found"
        );

        Certificate memory certificate =
            certificates[_certificateId];

        return (
            certificate.certificateId,
            certificate.studentName,
            certificate.course,
            certificate.institution,
            certificate.certificateHash,
            certificate.issueDate,
            certificate.issuer,
            certificate.revoked
        );
    }

    function revokeCertificate(
        string memory _certificateId
    )
        public
        onlyOwner
    {
        require(
            certificates[_certificateId].exists,
            "Certificate not found"
        );

        require(
            !certificates[_certificateId].revoked,
            "Certificate already revoked"
        );

        certificates[_certificateId].revoked = true;

        emit CertificateRevoked(
            _certificateId
        );
    }
}