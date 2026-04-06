openapi: 3.0.3
info:
  title: Event Management API
  version: 1.0.0
  description: API for managing technical events and conferences
paths:
  /api/v1/auth/login/:
    post:
      operationId: v1_auth_login_create
      description: |-
        Takes a set of user credentials and returns an access and refresh JSON web
        token pair to prove the authentication of those credentials.
      tags:
      - v1
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/TokenObtainPair'
          application/x-www-form-urlencoded:
            schema:
              $ref: '#/components/schemas/TokenObtainPair'
          multipart/form-data:
            schema:
              $ref: '#/components/schemas/TokenObtainPair'
        required: true
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TokenObtainPair'
          description: ''
  /api/v1/auth/logout/:
    post:
      operationId: v1_auth_logout_create
      tags:
      - v1
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Logout'
          application/x-www-form-urlencoded:
            schema:
              $ref: '#/components/schemas/Logout'
          multipart/form-data:
            schema:
              $ref: '#/components/schemas/Logout'
        required: true
      security:
      - jwtAuth: []
      responses:
        '204':
          description: No response body
  /api/v1/auth/me/:
    get:
      operationId: v1_auth_me_retrieve
      tags:
      - v1
      security:
      - jwtAuth: []
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
          description: ''
    put:
      operationId: v1_auth_me_update
      tags:
      - v1
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/User'
          application/x-www-form-urlencoded:
            schema:
              $ref: '#/components/schemas/User'
          multipart/form-data:
            schema:
              $ref: '#/components/schemas/User'
        required: true
      security:
      - jwtAuth: []
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
          description: ''
    patch:
      operationId: v1_auth_me_partial_update
      tags:
      - v1
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PatchedUser'
          application/x-www-form-urlencoded:
            schema:
              $ref: '#/components/schemas/PatchedUser'
          multipart/form-data:
            schema:
              $ref: '#/components/schemas/PatchedUser'
      security:
      - jwtAuth: []
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
          description: ''
  /api/v1/auth/refresh/:
    post:
      operationId: v1_auth_refresh_create
      description: |-
        Takes a refresh type JSON web token and returns an access type JSON web
        token if the refresh token is valid.
      tags:
      - v1
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/TokenRefresh'
          application/x-www-form-urlencoded:
            schema:
              $ref: '#/components/schemas/TokenRefresh'
          multipart/form-data:
            schema:
              $ref: '#/components/schemas/TokenRefresh'
        required: true
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TokenRefresh'
          description: ''
  /api/v1/auth/register/:
    post:
      operationId: v1_auth_register_create
      tags:
      - v1
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Register'
          application/x-www-form-urlencoded:
            schema:
              $ref: '#/components/schemas/Register'
          multipart/form-data:
            schema:
              $ref: '#/components/schemas/Register'
        required: true
      security:
      - jwtAuth: []
      - {}
      responses:
        '201':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Register'
          description: ''
  /api/v1/events/:
    get:
      operationId: v1_events_list
      parameters:
      - name: ordering
        required: false
        in: query
        description: Which field to use when ordering the results.
        schema:
          type: string
      - name: page
        required: false
        in: query
        description: A page number within the paginated result set.
        schema:
          type: integer
      - name: search
        required: false
        in: query
        description: A search term.
        schema:
          type: string
      - in: query
        name: start_from
        schema:
          type: string
          format: date-time
      - in: query
        name: start_to
        schema:
          type: string
          format: date-time
      - in: query
        name: status
        schema:
          type: string
      tags:
      - v1
      security:
      - jwtAuth: []
      - {}
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PaginatedEventListList'
          description: ''
    post:
      operationId: v1_events_create
      tags:
      - v1
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/EventWrite'
          application/x-www-form-urlencoded:
            schema:
              $ref: '#/components/schemas/EventWrite'
          multipart/form-data:
            schema:
              $ref: '#/components/schemas/EventWrite'
        required: true
      security:
      - jwtAuth: []
      responses:
        '201':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/EventWrite'
          description: ''
  /api/v1/events/{slug}/:
    get:
      operationId: v1_events_retrieve
      parameters:
      - in: path
        name: slug
        schema:
          type: string
        required: true
      tags:
      - v1
      security:
      - jwtAuth: []
      - {}
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/EventDetail'
          description: ''
    put:
      operationId: v1_events_update
      parameters:
      - in: path
        name: slug
        schema:
          type: string
        required: true
      tags:
      - v1
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/EventWrite'
          application/x-www-form-urlencoded:
            schema:
              $ref: '#/components/schemas/EventWrite'
          multipart/form-data:
            schema:
              $ref: '#/components/schemas/EventWrite'
        required: true
      security:
      - jwtAuth: []
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/EventWrite'
          description: ''
    patch:
      operationId: v1_events_partial_update
      parameters:
      - in: path
        name: slug
        schema:
          type: string
        required: true
      tags:
      - v1
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PatchedEventWrite'
          application/x-www-form-urlencoded:
            schema:
              $ref: '#/components/schemas/PatchedEventWrite'
          multipart/form-data:
            schema:
              $ref: '#/components/schemas/PatchedEventWrite'
      security:
      - jwtAuth: []
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/EventWrite'
          description: ''
    delete:
      operationId: v1_events_destroy
      parameters:
      - in: path
        name: slug
        schema:
          type: string
        required: true
      tags:
      - v1
      security:
      - jwtAuth: []
      responses:
        '204':
          description: No response body
  /api/v1/events/{slug}/register/:
    post:
      operationId: v1_events_register_create
      parameters:
      - in: path
        name: slug
        schema:
          type: string
        required: true
      tags:
      - v1
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/EventList'
          application/x-www-form-urlencoded:
            schema:
              $ref: '#/components/schemas/EventList'
          multipart/form-data:
            schema:
              $ref: '#/components/schemas/EventList'
        required: true
      security:
      - jwtAuth: []
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/EventList'
          description: ''
  /api/v1/events/{slug}/registrations/:
    get:
      operationId: v1_events_registrations_retrieve
      parameters:
      - in: path
        name: slug
        schema:
          type: string
        required: true
      tags:
      - v1
      security:
      - jwtAuth: []
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/EventList'
          description: ''
  /api/v1/events/{slug}/sessions/:
    get:
      operationId: v1_events_sessions_retrieve
      parameters:
      - in: path
        name: slug
        schema:
          type: string
        required: true
      tags:
      - v1
      security:
      - jwtAuth: []
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/EventList'
          description: ''
  /api/v1/events/{slug}/tracks/:
    get:
      operationId: v1_events_tracks_retrieve
      parameters:
      - in: path
        name: slug
        schema:
          type: string
        required: true
      tags:
      - v1
      security:
      - jwtAuth: []
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/EventList'
          description: ''
    post:
      operationId: v1_events_tracks_create
      parameters:
      - in: path
        name: slug
        schema:
          type: string
        required: true
      tags:
      - v1
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/EventList'
          application/x-www-form-urlencoded:
            schema:
              $ref: '#/components/schemas/EventList'
          multipart/form-data:
            schema:
              $ref: '#/components/schemas/EventList'
        required: true
      security:
      - jwtAuth: []
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/EventList'
          description: ''
  /api/v1/registrations/:
    get:
      operationId: v1_registrations_list
      parameters:
      - name: ordering
        required: false
        in: query
        description: Which field to use when ordering the results.
        schema:
          type: string
      - name: page
        required: false
        in: query
        description: A page number within the paginated result set.
        schema:
          type: integer
      - name: search
        required: false
        in: query
        description: A search term.
        schema:
          type: string
      tags:
      - v1
      security:
      - jwtAuth: []
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PaginatedRegistrationList'
          description: ''
    post:
      operationId: v1_registrations_create
      tags:
      - v1
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Registration'
          application/x-www-form-urlencoded:
            schema:
              $ref: '#/components/schemas/Registration'
          multipart/form-data:
            schema:
              $ref: '#/components/schemas/Registration'
        required: true
      security:
      - jwtAuth: []
      responses:
        '201':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Registration'
          description: ''
  /api/v1/registrations/{id}/:
    get:
      operationId: v1_registrations_retrieve
      parameters:
      - in: path
        name: id
        schema:
          type: integer
        description: A unique integer value identifying this registration.
        required: true
      tags:
      - v1
      security:
      - jwtAuth: []
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Registration'
          description: ''
    patch:
      operationId: v1_registrations_partial_update
      parameters:
      - in: path
        name: id
        schema:
          type: integer
        description: A unique integer value identifying this registration.
        required: true
      tags:
      - v1
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PatchedRegistration'
          application/x-www-form-urlencoded:
            schema:
              $ref: '#/components/schemas/PatchedRegistration'
          multipart/form-data:
            schema:
              $ref: '#/components/schemas/PatchedRegistration'
      security:
      - jwtAuth: []
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Registration'
          description: ''
  /api/v1/sessions/:
    get:
      operationId: v1_sessions_list
      parameters:
      - name: ordering
        required: false
        in: query
        description: Which field to use when ordering the results.
        schema:
          type: string
      - name: page
        required: false
        in: query
        description: A page number within the paginated result set.
        schema:
          type: integer
      - name: search
        required: false
        in: query
        description: A search term.
        schema:
          type: string
      - in: query
        name: session_type
        schema:
          type: string
          enum:
          - keynote
          - panel
          - talk
          - workshop
        description: |-
          * `talk` - Talk
          * `workshop` - Workshop
          * `panel` - Panel
          * `keynote` - Keynote
      - in: query
        name: speaker
        schema:
          type: integer
      - in: query
        name: start_from
        schema:
          type: string
          format: date-time
      - in: query
        name: start_to
        schema:
          type: string
          format: date-time
      - in: query
        name: track
        schema:
          type: integer
      tags:
      - v1
      security:
      - jwtAuth: []
      - {}
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PaginatedSessionList'
          description: ''
    post:
      operationId: v1_sessions_create
      tags:
      - v1
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Session'
          application/x-www-form-urlencoded:
            schema:
              $ref: '#/components/schemas/Session'
          multipart/form-data:
            schema:
              $ref: '#/components/schemas/Session'
        required: true
      security:
      - jwtAuth: []
      responses:
        '201':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Session'
          description: ''
  /api/v1/sessions/{id}/:
    get:
      operationId: v1_sessions_retrieve
      parameters:
      - in: path
        name: id
        schema:
          type: integer
        description: A unique integer value identifying this session.
        required: true
      tags:
      - v1
      security:
      - jwtAuth: []
      - {}
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Session'
          description: ''
    put:
      operationId: v1_sessions_update
      parameters:
      - in: path
        name: id
        schema:
          type: integer
        description: A unique integer value identifying this session.
        required: true
      tags:
      - v1
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Session'
          application/x-www-form-urlencoded:
            schema:
              $ref: '#/components/schemas/Session'
          multipart/form-data:
            schema:
              $ref: '#/components/schemas/Session'
        required: true
      security:
      - jwtAuth: []
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Session'
          description: ''
    patch:
      operationId: v1_sessions_partial_update
      parameters:
      - in: path
        name: id
        schema:
          type: integer
        description: A unique integer value identifying this session.
        required: true
      tags:
      - v1
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PatchedSession'
          application/x-www-form-urlencoded:
            schema:
              $ref: '#/components/schemas/PatchedSession'
          multipart/form-data:
            schema:
              $ref: '#/components/schemas/PatchedSession'
      security:
      - jwtAuth: []
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Session'
          description: ''
    delete:
      operationId: v1_sessions_destroy
      parameters:
      - in: path
        name: id
        schema:
          type: integer
        description: A unique integer value identifying this session.
        required: true
      tags:
      - v1
      security:
      - jwtAuth: []
      responses:
        '204':
          description: No response body
  /api/v1/speakers/:
    get:
      operationId: v1_speakers_list
      parameters:
      - name: ordering
        required: false
        in: query
        description: Which field to use when ordering the results.
        schema:
          type: string
      - name: page
        required: false
        in: query
        description: A page number within the paginated result set.
        schema:
          type: integer
      - name: search
        required: false
        in: query
        description: A search term.
        schema:
          type: string
      tags:
      - v1
      security:
      - jwtAuth: []
      - {}
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PaginatedSpeakerList'
          description: ''
    post:
      operationId: v1_speakers_create
      tags:
      - v1
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Speaker'
          application/x-www-form-urlencoded:
            schema:
              $ref: '#/components/schemas/Speaker'
          multipart/form-data:
            schema:
              $ref: '#/components/schemas/Speaker'
        required: true
      security:
      - jwtAuth: []
      responses:
        '201':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Speaker'
          description: ''
  /api/v1/speakers/{id}/:
    get:
      operationId: v1_speakers_retrieve
      parameters:
      - in: path
        name: id
        schema:
          type: integer
        description: A unique integer value identifying this speaker.
        required: true
      tags:
      - v1
      security:
      - jwtAuth: []
      - {}
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Speaker'
          description: ''
    put:
      operationId: v1_speakers_update
      parameters:
      - in: path
        name: id
        schema:
          type: integer
        description: A unique integer value identifying this speaker.
        required: true
      tags:
      - v1
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Speaker'
          application/x-www-form-urlencoded:
            schema:
              $ref: '#/components/schemas/Speaker'
          multipart/form-data:
            schema:
              $ref: '#/components/schemas/Speaker'
        required: true
      security:
      - jwtAuth: []
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Speaker'
          description: ''
    patch:
      operationId: v1_speakers_partial_update
      parameters:
      - in: path
        name: id
        schema:
          type: integer
        description: A unique integer value identifying this speaker.
        required: true
      tags:
      - v1
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PatchedSpeaker'
          application/x-www-form-urlencoded:
            schema:
              $ref: '#/components/schemas/PatchedSpeaker'
          multipart/form-data:
            schema:
              $ref: '#/components/schemas/PatchedSpeaker'
      security:
      - jwtAuth: []
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Speaker'
          description: ''
    delete:
      operationId: v1_speakers_destroy
      parameters:
      - in: path
        name: id
        schema:
          type: integer
        description: A unique integer value identifying this speaker.
        required: true
      tags:
      - v1
      security:
      - jwtAuth: []
      responses:
        '204':
          description: No response body
  /api/v1/tracks/:
    get:
      operationId: v1_tracks_list
      parameters:
      - name: ordering
        required: false
        in: query
        description: Which field to use when ordering the results.
        schema:
          type: string
      - name: page
        required: false
        in: query
        description: A page number within the paginated result set.
        schema:
          type: integer
      - name: search
        required: false
        in: query
        description: A search term.
        schema:
          type: string
      tags:
      - v1
      security:
      - jwtAuth: []
      - {}
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PaginatedTrackList'
          description: ''
  /api/v1/tracks/{id}/:
    get:
      operationId: v1_tracks_retrieve
      parameters:
      - in: path
        name: id
        schema:
          type: integer
        description: A unique integer value identifying this track.
        required: true
      tags:
      - v1
      security:
      - jwtAuth: []
      - {}
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Track'
          description: ''
    put:
      operationId: v1_tracks_update
      parameters:
      - in: path
        name: id
        schema:
          type: integer
        description: A unique integer value identifying this track.
        required: true
      tags:
      - v1
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Track'
          application/x-www-form-urlencoded:
            schema:
              $ref: '#/components/schemas/Track'
          multipart/form-data:
            schema:
              $ref: '#/components/schemas/Track'
        required: true
      security:
      - jwtAuth: []
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Track'
          description: ''
    patch:
      operationId: v1_tracks_partial_update
      parameters:
      - in: path
        name: id
        schema:
          type: integer
        description: A unique integer value identifying this track.
        required: true
      tags:
      - v1
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PatchedTrack'
          application/x-www-form-urlencoded:
            schema:
              $ref: '#/components/schemas/PatchedTrack'
          multipart/form-data:
            schema:
              $ref: '#/components/schemas/PatchedTrack'
      security:
      - jwtAuth: []
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Track'
          description: ''
    delete:
      operationId: v1_tracks_destroy
      parameters:
      - in: path
        name: id
        schema:
          type: integer
        description: A unique integer value identifying this track.
        required: true
      tags:
      - v1
      security:
      - jwtAuth: []
      responses:
        '204':
          description: No response body
components:
  schemas:
    EventDetail:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        title:
          type: string
          maxLength: 255
        slug:
          type: string
          maxLength: 280
          pattern: ^[-a-zA-Z0-9_]+$
        description:
          type: string
        start_date:
          type: string
          format: date-time
        end_date:
          type: string
          format: date-time
        venue_name:
          type: string
          maxLength: 255
        venue_address:
          type: string
        max_attendees:
          type: integer
          maximum: 2147483647
          minimum: 0
        status:
          $ref: '#/components/schemas/EventStatusEnum'
        banner:
          type: string
          format: uri
          nullable: true
        organizer_name:
          type: string
          readOnly: true
        tracks:
          type: array
          items:
            $ref: '#/components/schemas/Track'
          readOnly: true
        created_at:
          type: string
          format: date-time
          readOnly: true
        updated_at:
          type: string
          format: date-time
          readOnly: true
      required:
      - created_at
      - description
      - end_date
      - id
      - max_attendees
      - organizer_name
      - start_date
      - title
      - tracks
      - updated_at
      - venue_address
      - venue_name
    EventList:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        title:
          type: string
          maxLength: 255
        slug:
          type: string
          maxLength: 280
          pattern: ^[-a-zA-Z0-9_]+$
        start_date:
          type: string
          format: date-time
        end_date:
          type: string
          format: date-time
        venue_name:
          type: string
          maxLength: 255
        max_attendees:
          type: integer
          maximum: 2147483647
          minimum: 0
        status:
          $ref: '#/components/schemas/EventStatusEnum'
        banner:
          type: string
          format: uri
          nullable: true
        organizer_name:
          type: string
          readOnly: true
      required:
      - end_date
      - id
      - max_attendees
      - organizer_name
      - start_date
      - title
      - venue_name
    EventStatusEnum:
      enum:
      - draft
      - published
      - cancelled
      type: string
      description: |-
        * `draft` - Draft
        * `published` - Published
        * `cancelled` - Cancelled
    EventWrite:
      type: object
      properties:
        title:
          type: string
          maxLength: 255
        description:
          type: string
        start_date:
          type: string
          format: date-time
        end_date:
          type: string
          format: date-time
        venue_name:
          type: string
          maxLength: 255
        venue_address:
          type: string
        max_attendees:
          type: integer
          maximum: 2147483647
          minimum: 0
        status:
          $ref: '#/components/schemas/EventStatusEnum'
        banner:
          type: string
          format: uri
          nullable: true
      required:
      - description
      - end_date
      - max_attendees
      - start_date
      - title
      - venue_address
      - venue_name
    Logout:
      type: object
      properties:
        refresh:
          type: string
      required:
      - refresh
    PaginatedEventListList:
      type: object
      required:
      - count
      - results
      properties:
        count:
          type: integer
          example: 123
        next:
          type: string
          nullable: true
          format: uri
          example: http://api.example.org/accounts/?page=4
        previous:
          type: string
          nullable: true
          format: uri
          example: http://api.example.org/accounts/?page=2
        results:
          type: array
          items:
            $ref: '#/components/schemas/EventList'
    PaginatedRegistrationList:
      type: object
      required:
      - count
      - results
      properties:
        count:
          type: integer
          example: 123
        next:
          type: string
          nullable: true
          format: uri
          example: http://api.example.org/accounts/?page=4
        previous:
          type: string
          nullable: true
          format: uri
          example: http://api.example.org/accounts/?page=2
        results:
          type: array
          items:
            $ref: '#/components/schemas/Registration'
    PaginatedSessionList:
      type: object
      required:
      - count
      - results
      properties:
        count:
          type: integer
          example: 123
        next:
          type: string
          nullable: true
          format: uri
          example: http://api.example.org/accounts/?page=4
        previous:
          type: string
          nullable: true
          format: uri
          example: http://api.example.org/accounts/?page=2
        results:
          type: array
          items:
            $ref: '#/components/schemas/Session'
    PaginatedSpeakerList:
      type: object
      required:
      - count
      - results
      properties:
        count:
          type: integer
          example: 123
        next:
          type: string
          nullable: true
          format: uri
          example: http://api.example.org/accounts/?page=4
        previous:
          type: string
          nullable: true
          format: uri
          example: http://api.example.org/accounts/?page=2
        results:
          type: array
          items:
            $ref: '#/components/schemas/Speaker'
    PaginatedTrackList:
      type: object
      required:
      - count
      - results
      properties:
        count:
          type: integer
          example: 123
        next:
          type: string
          nullable: true
          format: uri
          example: http://api.example.org/accounts/?page=4
        previous:
          type: string
          nullable: true
          format: uri
          example: http://api.example.org/accounts/?page=2
        results:
          type: array
          items:
            $ref: '#/components/schemas/Track'
    PatchedEventWrite:
      type: object
      properties:
        title:
          type: string
          maxLength: 255
        description:
          type: string
        start_date:
          type: string
          format: date-time
        end_date:
          type: string
          format: date-time
        venue_name:
          type: string
          maxLength: 255
        venue_address:
          type: string
        max_attendees:
          type: integer
          maximum: 2147483647
          minimum: 0
        status:
          $ref: '#/components/schemas/EventStatusEnum'
        banner:
          type: string
          format: uri
          nullable: true
    PatchedRegistration:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        event:
          type: string
        attendee:
          type: string
          readOnly: true
        registered_at:
          type: string
          format: date-time
          readOnly: true
        status:
          allOf:
          - $ref: '#/components/schemas/RegistrationStatusEnum'
          readOnly: true
    PatchedSession:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        title:
          type: string
          maxLength: 255
        description:
          type: string
        track:
          type: integer
        speaker:
          type: integer
          nullable: true
        start_time:
          type: string
          format: date-time
        end_time:
          type: string
          format: date-time
        room:
          type: string
          maxLength: 255
        session_type:
          $ref: '#/components/schemas/SessionTypeEnum'
        capacity:
          type: integer
          maximum: 2147483647
          minimum: 0
          nullable: true
        effective_capacity:
          type: integer
          nullable: true
          readOnly: true
    PatchedSpeaker:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        name:
          type: string
          maxLength: 255
        bio:
          type: string
        photo:
          type: string
          format: uri
          nullable: true
        company:
          type: string
          maxLength: 255
        website:
          type: string
          format: uri
          maxLength: 200
        user:
          type: integer
          nullable: true
    PatchedTrack:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        event:
          type: integer
          readOnly: true
        name:
          type: string
          maxLength: 255
        description:
          type: string
        color:
          type: string
          maxLength: 7
    PatchedUser:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        email:
          type: string
          format: email
          readOnly: true
        name:
          type: string
          maxLength: 255
        bio:
          type: string
        avatar:
          type: string
          format: uri
          nullable: true
        is_organizer:
          type: boolean
    Register:
      type: object
      properties:
        email:
          type: string
          format: email
          maxLength: 254
        name:
          type: string
          maxLength: 255
        password:
          type: string
          writeOnly: true
          minLength: 8
        is_organizer:
          type: boolean
      required:
      - email
      - name
      - password
    Registration:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        event:
          type: string
        attendee:
          type: string
          readOnly: true
        registered_at:
          type: string
          format: date-time
          readOnly: true
        status:
          allOf:
          - $ref: '#/components/schemas/RegistrationStatusEnum'
          readOnly: true
      required:
      - attendee
      - event
      - id
      - registered_at
      - status
    RegistrationStatusEnum:
      enum:
      - confirmed
      - cancelled
      - waitlisted
      type: string
      description: |-
        * `confirmed` - Confirmed
        * `cancelled` - Cancelled
        * `waitlisted` - Waitlisted
    Session:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        title:
          type: string
          maxLength: 255
        description:
          type: string
        track:
          type: integer
        speaker:
          type: integer
          nullable: true
        start_time:
          type: string
          format: date-time
        end_time:
          type: string
          format: date-time
        room:
          type: string
          maxLength: 255
        session_type:
          $ref: '#/components/schemas/SessionTypeEnum'
        capacity:
          type: integer
          maximum: 2147483647
          minimum: 0
          nullable: true
        effective_capacity:
          type: integer
          nullable: true
          readOnly: true
      required:
      - description
      - effective_capacity
      - end_time
      - id
      - start_time
      - title
      - track
    SessionTypeEnum:
      enum:
      - talk
      - workshop
      - panel
      - keynote
      type: string
      description: |-
        * `talk` - Talk
        * `workshop` - Workshop
        * `panel` - Panel
        * `keynote` - Keynote
    Speaker:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        name:
          type: string
          maxLength: 255
        bio:
          type: string
        photo:
          type: string
          format: uri
          nullable: true
        company:
          type: string
          maxLength: 255
        website:
          type: string
          format: uri
          maxLength: 200
        user:
          type: integer
          nullable: true
      required:
      - bio
      - id
      - name
    TokenObtainPair:
      type: object
      properties:
        email:
          type: string
          writeOnly: true
        password:
          type: string
          writeOnly: true
        access:
          type: string
          readOnly: true
        refresh:
          type: string
          readOnly: true
      required:
      - access
      - email
      - password
      - refresh
    TokenRefresh:
      type: object
      properties:
        access:
          type: string
          readOnly: true
        refresh:
          type: string
      required:
      - access
      - refresh
    Track:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        event:
          type: integer
          readOnly: true
        name:
          type: string
          maxLength: 255
        description:
          type: string
        color:
          type: string
          maxLength: 7
      required:
      - event
      - id
      - name
    User:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        email:
          type: string
          format: email
          readOnly: true
        name:
          type: string
          maxLength: 255
        bio:
          type: string
        avatar:
          type: string
          format: uri
          nullable: true
        is_organizer:
          type: boolean
      required:
      - email
      - id
      - name
  securitySchemes:
    jwtAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
